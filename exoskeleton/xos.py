"""
STANDARD LIBRARIES
"""
import random

import pandas as pd  # Critical, most of the data structures are pandas structures
import asyncio  # For asynchronous OSC handling

"""
OTHER LIBRARIES
"""

"""
KLAMPT IMPORTS
"""

import klampt  # Main robotics library
import klampt.vis  # For visualization
import klampt.vis.colorize  # For colorizing to easily assess robot performance
import klampt.sim.batch  # For batch simulation
import klampt.sim.settle  # Applies forces and lets them reach equilibrium in simulation
import klampt.sim.simulation  # For simulation
import klampt.io.resource  # For easy resource access
import klampt.model.subrobot  # Defines the subrobot
import klampt.math.vectorops as kmv  # This is for cross products

"""
CUSTOM LIBRARIES
"""
import pyonics.submodules.ui.interface as ui  # Interface modules
import pyonics.submodules.control.control as ctrl

"""
PANDAS CONFIG
"""
pd.options.display.width = 0
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# General Configuration
def configLoader(config_name):
    """
    This is tightly coupled with the GUNDAM (limb/element-wise) style configuration process.
    Takes configuration filepath as an argument.

    Returns a dataframe with entries in columns referencing the filepath of the robot core, and of the location of
    the muscle attachments CSV.
    """
    print("Loading configuration" + config_name + "...\n")
    with open(config_name) as fn:
        print("Loading core components...\n", fn.readline().rstrip())
        core = fn.readline().rstrip()  # Filepath to robot core
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
        print("Setting display resolution...\n", fn.readline().rstrip())
        width = int(fn.readline().rstrip())
        height = int(fn.readline().rstrip())
        print("Selecting voice ID...\n", fn.readline().rstrip())
        voice_id = int(fn.readline().strip())
        print("Setting voice speech rate\n", fn.readline().strip())
        voice_rate = int(fn.readline().rstrip())
        config = {"core": core,
                  "attachments": attachments,
                  "world_path": world_path,
                  "timestep": timestep,
                  "address": address,
                  "port": port,
                  "width": width,
                  "height": height,
                  "voice_id": voice_id,
                  "voice_rate": voice_rate}

        return config

"""
CLASS DEFINITIONS
"""

"""
Operating System
"""
class ExOS(klampt.control.OmniRobotInterface):
    """
    High level controller. Should abstract away most of the implementation details. Want plug and play.
    """

    # Initialization
    def __init__(self, config_data, has_klampt=True, has_hud=True, has_persona=False, has_voice=True):
        """
        Initializes the controller. Should work on a physical or simulated robot equivalently or simultaneously.
        """
        self.shutdown_flag = False
        self.state = "On"
        self.input = None
        self.dt = None

        if has_persona:
            self.persona = ui.Personality()  # Creates a personality
        else:
            self.persona = None

        if has_voice:
            self.voice = ui.VoiceAssistantUI(config_data["voice_id"], config_data["voice_rate"])
        else:
            self.voice = None

        if has_klampt:
            self.robot = ctrl.ExoController(config_data).robot
            self.world = self.robot.world
        else:
            self.robot = None
            self.world = None

        if has_hud:
            self.hud = ui.AugmentOverlayKlUI()  # Should be a place for a HUD object
        else:
            self.hud = None

        klampt.control.OmniRobotInterface.__init__(self, self.robot)
        asyncio.run(self.hud.idle())

    async def main(self):
        # Main operating system loop.
        # Voice intake
        if self.voice:
            self.input = self.voice.voice_loop()
        else:
            self.input = "blahdy blah blah blah"

        # Personality processing
        if self.persona:
            response = self.persona.process_input(self.input)
        else:
            response = ""

        # Vocalization of processed response
        if self.voice:
            self.voice.announce(response)
        else:
            pass

        await self.hud.idle()
        return "Running..."

    async def safe_mode(self):
        self.state = "In Safe Mode (Restricted)"

    async def async_error(self):
        if self.voice:
            self.voice.announce("Error:")
            self.voice.announce(ui.sysvx.negatives[random.randint(0,len(ui.sysvx.negatives))])



    # Control and Kinematics

    def sensedPosition(self):
        """
        Returns the list of link transforms, and???
        """
        return [0,0,0]

    def controlRate(self):
        """
        Should be the same as the physical device, Reaktor control rate, simulation timestep
        """
        return self.dt

    def shutdown(self):
        # Should shut everything down nice and pretty.
        self.shutdown_flag = True
        self.voice.announce("Shutting down systems.")
        self.hud.async_shutdown()

"""
Boot Modes
"""
class SafeMode(ExOS):
    def __init__(self, config_data):
        ExOS.__init__(self, config_data)

    async def main(self):
        # Main safe boot loop
        return None
"""
Simulation
"""
class ExoSim(klampt.sim.simulation.SimpleSimulator):
    """
    This is a class for Simulations. It will contain the substepping logic where forces are applied to simulated objects.
    """
    def __init__(self, wm, robot, timestep):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.dt = timestep
        self.world = wm
        self.robotmodel = robot
        self.link_transforms_start = [self.robotmodel.link(x).getTransform() for x in range(self.robotmodel.numLinks())]
        self.link_transforms_end = None
        self.link_transforms_diff = None


    def simLoop(self, force_list):
        """
        robot: A RobotModel.
        force_list: Not sure what data structure, maybe a dataframe? name of muscle as index, with force and transform

        Should possibly return a list of new transforms to be used for calculating stuff in the next time step.

        """
        wm = self.world

        self.link_transforms_start = [self.robotmodel.link(x).getTransform() for x in range(self.robotmodel.numLinks())]
        """
        Now here adding a section to make sure the muscles contract in the simulation.
        """
        for force in force_list:
            link = self.body(self.robotmodel.link(force[0]))  # From the force info, gets the link to apply force
            force_vector = force[1]  # Gets the force vector
            transform = force[2]  # Gets the transform at which to apply force
            link.applyForceAtLocalPoint(force_vector, transform)

        self.simulate(self.dt)
        self.updateWorld()
        """
        Maybe here is where we have to get the updated link transforms and return them as "sensor" feedback.
        """
        self.link_transforms_end = [self.robotmodel.link(x).getTransform() for x in range(self.robotmodel.numLinks())]

        self.link_transforms_diff = [klampt.math.se3.error(self.link_transforms_start[x], self.link_transforms_end[x])
                                for x in range(len(self.link_transforms_start))]  # Takes the Lie derivative from start -> end
        return self.link_transforms_end  # I don't even know if we need to use this, depends on if we pass by ref or var

"""
MAIN LOOP
"""
def initialize(config_filepath):
    config = configLoader(config_filepath)
    #mode = input("What mode would you like to launch in?: ")
    mode = ""
    match mode:
        case "safe":
            exo_test = SafeMode(config)
        case _:
            exo_test = ExOS(config)



if __name__ == "__main__":
    initialize("test_config3.txt")