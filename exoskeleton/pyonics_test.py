import klampt
import klampt.vis
import klampt.io
import pyonics
from pyonics.control.messages import AsyncServer, AsyncTestClient

import asyncio
from datetime import datetime

import utils.apps as xapp
import utils.ui as ui
import utils.video as vid

def basic_config(config_name):
    """
        This is tightly coupled with the GUNDAM (limb/element-wise) style configuration process.
        Takes configuration filepath as an argument.

        Returns a dataframe with entries in columns referencing the filepath of the robot core, and of the location of
        the muscle attachments CSV.

        Want to add a "has simulation" parameter.
        """
    print("Loading configuration" + config_name + "...\n")
    with open(config_name) as fn:
        print("Loading core components...\n", fn.readline().rstrip())
        core = fn.readline().rstrip()  # Filepath to robot core
        print("Locating model data...\n", fn.readline().rstrip())
        model = fn.readline().rstrip()  # Filepath to calculated model parameters
        print("Loading muscle attachments...\n", fn.readline().rstrip())
        attachments = fn.readline().rstrip()  # Filepath to muscle attachments file
        print("Locating world filepath...\n", fn.readline().rstrip())
        world_path = fn.readline().rstrip()  # Filepath to the world file
        print("Configuring control rates...\n", fn.readline().rstrip())
        timestep = float(fn.readline().rstrip())  # Float value setting simulation and control time step; want >.01 sec
        print("Setting controller address...\n", fn.readline().rstrip())
        address = fn.readline().rstrip()  # Controller IP address; string value
        print("Setting controller network socket...\n", fn.readline().rstrip())
        port = int(fn.readline().rstrip())  # Controller network socket
        print("Setting network mode...\n", fn.readline().rstrip())
        network_mode = fn.readline().rstrip()
        print("Setting display resolution...\n", fn.readline().rstrip())
        width = int(fn.readline().rstrip())
        height = int(fn.readline().rstrip())
        print("Getting world preferences...\n", fn.readline().rstrip())
        has_robworld = eval(str(fn.readline().rstrip()))
        print("Getting visualization preferences...\n", fn.readline().rstrip())
        has_vis = eval(str(fn.readline().rstrip()))
        print("Getting simulation preferences...\n", fn.readline().rstrip())
        has_sim = eval(str(fn.readline().rstrip()))
        config = {"core": core,
                  "model": model,
                  "attachments": attachments,
                  "world_path": world_path,
                  "timestep": timestep,
                  "address": address,
                  "port": port,
                  "network_mode": network_mode,
                  "width": width,
                  "height": height,
                  "has_robworld": has_robworld,
                  "has_vis": has_vis,
                  "has_sim": has_sim,
                  }
    return config

class BasicExo():
    """
    High level controller. Should abstract away most of the implementation details. Want plug and play.
    """

    # Initialization
    def __init__(self, config_data):
        """S
        Initializes the controller. Should work on a physical or simulated robot equivalently or simultaneously.
        """
        self.model_path = config_data["model"]

        self.network_mode = config_data["network_mode"]  # Can be master or slave
        self.dt = config_data["timestep"]

        if config_data["has_robworld"]:
            # Variable for a robot representation # Not sure if this is happening correctly
            self.pcm = pyonics.ExoController(config_data) # PCM as in powertrain control module, this is primary motor driver
            self.input = asyncio.run(self.pcm.idle(self.pcm.bones))  # async function

        if config_data["has_sim"]:  # If a simulation is defined
            self.sim = xapp.Sim(self.pcm.world, self.pcm.robot, self.pcm.controlRate())
            self.sim.enableContactFeedbackAll()
            # asyncio.run(self.sim_settings())
            #self.sim.endLogging()
        else:
            self.sim = None

        # Visualization

        if config_data["has_vis"]:  # If there's a visualization
            klampt.vis.add("w", self.pcm.world)
            klampt.vis.add("robby", self.pcm.robot)

            if config_data["has_sim"]:  # If a simulation is defined AND there's a visualization
                vid.display_muscles(self.pcm.muscles)  # Displays the muscles

            klampt.vis.visualization.setWindowTitle("ExOS")
            klampt.vis.visualization.setBackgroundColor(.8, .5, .8, .3)

            klampt.vis.visualization.resizeWindow(1920, 1080)
            self.viewport = klampt.vis.getViewport()
            vid.configure_sim_vis(self.viewport)
            klampt.vis.show()  # Shows the visualization
            klampt.vis.spin(2) # argument is duration in seconds
        else:
            self.viewport = None

        klampt.control.OmniRobotInterface.__init__(self, self.pcm.robot)

        #self.logging = True  # This is the diagnostic output flag

        """
        This call to main needs to happen but it should happen after startup
        """
        # asyncio.run(self.startup(self.main))  # Initiates the primary idle loop for the total system
        # asyncio.run(self.startup(self.sim_test)) # Using the test method for debugging
        # klampt.vis.add("Config Space", self.pcm.cspace)  # Trying to show the configuration space.

    async def startup(self):
        """
        Should be called with the runtime loop to be started plus some conditionals to ensure are true
        """
        """
        Between these two state update commands should go the startup logic
        """
        # self.pcm.setCollisionFilter(world=None, op="warn")  # This makes the robot check for self-collisions and ignore commands that cause them
        if self.sim:
            await self.sim.configure_sim()
        await self.pcm.setup_osc_server()
        await vid.display_bones(self.pcm.robot)
        await self.pcm.server.enable_osc_logging()
        while klampt.vis.shown():  # I ddn't know if this should be packaged somehow
            await self.main()  # Async function call
            await asyncio.sleep(self.dt)
            # i += 1
            # asyncio.run(asyncio.sleep(1))

    async def main(self):
        # Diagnostics go here at the top
        # await vid.display_contact_forces(self.pcm.robot, self.sim)
        if self.sim:
            # Attend to the simulation
            # await self.collision_settings()  # Should access the collision settings function and do something related to collisions every loop
            if klampt.vis.shown():
                vid.display_muscles(self.pcm.muscles)
                klampt.vis.lock()

            # Main operating system loop. Last argument of pressures_to_forces is a force multiplier.
            # forces = await self.pcm.pressures_to_forces(self.pcm.muscles.muscle_objects, self.pcm.pressures, 2)
            await test_constant()
            self.pcm.bones = await self.sim.testSimLoop()  # Needs list of input values
            for pressure in self.pcm.pressures:
                print(pressure)

            if klampt.vis.shown():
                klampt.vis.unlock()
                klampt.vis.update()

        else:
            pass

    async def async_error(self, error_message: None):
        print("ERROR")
        print(error_message)

    async def collision_settings(self):
        contacts = klampt.model.contact.sim_contact_map(self.sim)
        return contacts

    """
    Control
    """
    def sensedPosition(self):
        """
        Returns the list of link transforms, and???
        """
        return self.pcm.bones, self.pcm.muscles

    def controlRate(self):
        """
        Should be the same as the physical device, Reaktor control rate, simulation timestep
        """
        return self.dt

    def shutdown(self):
        # Should shut everything down nice and pretty.
        self.log_file.close()

    """
    Testing
    """
    async def sim_test(self):
        if self.sim:
            # Attend to the simulation
            # await self.collision_settings()  # Should access the collision settings function and do something related to collisions every loop
            if klampt.vis.shown():
                vid.display_muscles(self.pcm.muscles)
                klampt.vis.lock()

            # Main operating system loop. Last argument of pressures_to_forces is a force multiplier. (why?)
            # forces = await self.sim.pressures_to_forces(self.pcm.muscles.muscle_objects, self.pcm.pressures, 2)
            # self.pcm.bones = await self.sim.testSimLoop(forces)
            await self.sim.testSimLoop()

            if klampt.vis.shown():
                klampt.vis.unlock()
                klampt.vis.update()
        else:
            pass

    async def trajectory_test(self):
        return


    """
    Diagnostics
    """

"""
Testing Functions
"""


async def test_constant():
    client = AsyncTestClient(port=5005)

    def constant(t):
        return [50, 50, 50]

    await client.send_loop(constant, dt=0.1, duration=2.0)

def basic_launch():
    """
    Convenience launcher for current dev environment for Windows. Works as a simulation at the moment.
    """
    config = basic_config("config/basic_testconfig_sim.txt")
    exo_program = BasicExo(config)

if __name__ == "__main__":

    basic_launch()