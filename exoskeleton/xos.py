"""
STANDARD LIBRARIES
"""

import time
import vosk  # Voice recognition offline toolkit
import math  # Largely just used for pi right now
import numpy as np  # Just in case for now
import tkinter as tk  # For building desktopGUI
import pandas as pd  # Critical, most of the data structures are pandas structures
import asyncio  # For asynchronous OSC handling

"""
OTHER LIBRARIES
"""
import gpsd

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
import pyonics.submodules.network.osc_toolkit as osck  # OSC protocols for control
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

"""
FUNCTION DEFINITIONS
"""

# General Configuration
def configLoader(config_name):
    """
    This is tightly coupled with the GUNDAM (limb/element-wise) style configuration process.
    Takes configuration filepath as an argument.

    Returns a dataframe with entries in columns referencing the filepath of the robot core, and of the location of
    the muscle attachments CSV.
    """
    print("Loading configuration" + config_name + "...")
    with open(config_name) as fn:
        print("Loading core components...", fn.readline().rstrip())
        core = fn.readline().rstrip()  # Filepath to robot core
        print("Loading muscle attachments...", fn.readline().rstrip())
        attachments = fn.readline().rstrip()  # Filepath to muscle attachments file
        print("Locating world filepath...", fn.readline().rstrip())
        world_path = fn.readline().rstrip()  # Filepath to the world file
        print("Configuring control rates...", fn.readline().rstrip())
        timestep = float(fn.readline().rstrip())  # Float value setting simulation and control time step; want >.01 sec
        print("Setting controller address...", fn.readline().rstrip())
        address = fn.readline().rstrip()  # Controller IP address; string value
        print("Setting controller network socket...", fn.readline().rstrip())
        port = int(fn.readline().rstrip())  # Controller network socket
        print("Setting display resolution...", fn.readline().rstrip())
        width = int(fn.readline().rstrip())
        height = int(fn.readline().rstrip())
        print("Selecting voice ID...", fn.readline().rstrip())
        voice_id = int(fn.readline().strip())
        print("Setting voice speech rate", fn.readline().strip())
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
Controllers
"""
class ExOS(klampt.control.OmniRobotInterface):
    """
    High level controller. Should abstract away most of the implementation details. Want plug and play.
    """

    # Initialization
    def __init__(self, config_data):
        """
        Initializes the controller. Should work on a physical or simulated robot equivalently or simultaneously.
        """
        self.shutdown_flag = False
        self.input = None
        self.dt = None
        self.voice = ui.VoiceAssistantUI(1, 150)
        self.robot = ctrl.ExoController(config_data).robot
        self.world = self.robot.world
        self.hud = ui.AugmentOverlayKlUI()  # Should be a place for a HUD object
        klampt.control.OmniRobotInterface.__init__(self, self.robot)

    async def main_OS(self):
        return False

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
        self.hud.shutdown()

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
Launch Modes
"""
class ExoSimGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    This is a GUI that runs a simulation too. It should not have a HUD, it is for external simulation only.
    """
    def __init__(self, config):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        # All the world elements MUST be loaded before the Simulator is created

        klampt.vis.setWindowTitle("X001  Test")
        klampt.vis.setBackgroundColor(0, 0, 0, 1)  # Makes background black


        # Sets window to configured width and height
        # klampt.vis.resizeWindow(int(config["width"]),int(config["height"]))
        self.viewport = klampt.vis.getViewport()
        self.viewport.fit([0, 0, -5], 25)


        # creation of the controller, using the low level one
        self.controller = ctrl.ExoController(config)
        klampt.vis.add("world", self.controller.world)
        klampt.vis.add("X001", self.controller.robot)
        self.assistant = self.controller.assistant
        # creation of the simulation
        self.sim = ExoSim(self.controller.world, self.controller.robot, config["timestep"])

        self.drawMuscles()
        self.drawOptions()
        # Simulator creation and activation comes at the very end
        self.sim.setGravity([0, 0, -9.8])
        self.link_transforms = [self.robot.link(x).getTransform() for x in range(self.robot.numLinks())]  # Initialized
        # Begin desktopGUI event loop
        asyncio.run(self.idle_launcher())

    async def update_GUI(self):
        """
        Idle function for the desktopGUI that sends commands to the controller, gets forces from it, and sends to the sim.
        """
        self.hud.refresh()  # Refreshes the HUD
        klampt.vis.lock()  # Locks the klampt visualization
        forces = self.controller.idle(self.link_transforms)  # Gets new forces by sending transforms to simulator
        print(forces)
        self.link_transforms = self.sim.simLoop(forces)  # Takes forces and returns new positions
        self.drawMuscles()  # Should be changing draw options for the muscles
        klampt.vis.unlock()  # Unlocks the klampt visualization
        return True

    async def async_handler(self):
        #print(self.controller.input)
        while klampt.vis.shown():
            await self.update_GUI()  # Updates what is displayed
            await asyncio.sleep(0)  # Waits a bit to relinquish control to the OSC handler

    async def idle_launcher(self):
        """
        Asynchronous idle function. Creates server endpoint, launches visualization and begins simulation idle loop.
        """

        await self.controller.osc_handler.make_endpoint()  # Sets up OSC handler endpoint
        klampt.vis.show()  # Opens the visualization for the first time
        await self.async_handler()  # Performs asynchronous idle actions
        self.controller.osc_handler.transport.close()  # Closes the network socket once GUI is finished
        return True

    """
    Visual Options
    """
    def drawOptions(self):
        """
        Changes some drawing options for link geometry
        In the setDraw function, the first argument is an integer denoting vertices, edges. etc. The second is a Boolean
        determining regardless of whether the option is drawn.

        setColor function takes an int and RGBA float values.
        """
        wm = self.world
        for x in range(wm.numIDs()):
            wm.appearance(x).setDraw(2, True)  # Makes edges visible
            #wm.appearance(x).setDraw(4, True)  # I believe this should make edges glow
            wm.appearance(x).setColor(2, 0, 1, 0, .5)  # Makes edges green?
            #wm.appearance(x).setColor(4, .1, .1, .1, .1)  # This makes the faces a translucent blue grey
            #wm.appearance(x).setColor(4, 0, 1, 0, .5)  # I think this changes the glow color

    def drawMuscles(self):
        """
        This function takes all the muscles from the controller dataframe and draws them in the visualization
        """
        muscle_df = self.controller.muscles
        for row in muscle_df.itertuples():
            ui.visMuscles(row)

    """
    Shutdown
    """
    async def shutdown(self):
        self.hud.close_all()
        klampt.vis.kill()


"""
MAIN LOOP
"""
def initialize(config_filepath):
    config = configLoader(config_filepath)
    exo_test1 = ExOS(config)
    #exo_test2 = ExoSimGUI(config).customUI()


if __name__ == "__main__":
    initialize("test_config2.txt")