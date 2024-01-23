"""
STANDARD LIBRARIES
"""
import random
import platform  # For detecting the platform and automatically selecting the correct launcher

import pandas as pd  # Critical, most of the data structures are pandas structures
import asyncio  # For asynchronous OSC handling
import os # For listing files in directory
import sys
import logging
import tkinter as tk
import tkinter.filedialog as filedialog

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
import pyonics.submodules.video.video as vid
import pyonics.submodules.control.control as ctrl
import pyonics.submodules.apps.apps as xapp

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

    Want to add a "has simulation" parameter.
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
        print("Getting HUD preferences...\n", fn.readline().rstrip())
        has_hud = eval(str(fn.readline().rstrip()))
        print("Getting voice preferences...\n", fn.readline().rstrip())
        has_voice = eval(str(fn.readline().rstrip()))
        print("Setting personality...\n", fn.readline().rstrip())
        has_persona = eval(str(fn.readline().rstrip()))
        print("has persona is..." + str(has_persona))
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
                  "network_mode": network_mode,
                  "width": width,
                  "height": height,
                  "has_robworld": has_robworld,
                  "has_vis": has_vis,
                  "has_sim": has_sim,
                  "has_hud": has_hud,
                  "has_voice": has_voice,
                  "has_persona": has_persona,
                  "voice_id": voice_id,
                  "voice_rate": voice_rate
                  }

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
    def __init__(self, config_data):
        """
        Initializes the controller. Should work on a physical or simulated robot equivalently or simultaneously.
        """

        self.shutdown_flag = False
        self.state = "Initializing..."
        # Should be updated whenever something is happening to the whole system, made to be human-readable.

        self.mode = None  # Safe mode, restricted mode, etc. - None is normal
        self.network_mode = config_data["network_mode"]  # Can be master or slave
        self.input = "test string"
        self.dt = config_data["timestep"]

        # if config_data["has_persona"]:
        #     print("Value of has persona: " + str(config_data["has_persona"]))
        #     self.persona = ui.Personality()  # Creates a personality
        # else:
        #     self.persona = None

        if config_data["has_voice"]:
            print(config_data["has_voice"])
            self.voice = ui.VoiceAssistantUI(config_data["voice_id"], config_data["voice_rate"])
        else:
            self.voice = None

        # Simulation requires robworld. Robworld is necessary but insufficient to create simulation.
        if config_data["has_robworld"]:
            print("Initializing RobWorld...")
            # Variable for a robot representation # Not sure if this is happening correctly
            self.pcm = ctrl.ExoController(config_data) # PCM as in powertrain control module
            self.robot = self.pcm.robot
            self.world = self.pcm.world
            print(" . . . i n i t i a l i z i n g w o r l d . . . ")
        else:
            self.robot = self.pcm.robot
            self.world = self.robot.world

        if config_data["has_sim"]:
            self.sim = xapp.Sim(self.world, self.robot, self.dt)
        else:
            self.sim = xapp.Sim(self.world, self.robot, self.dt)


        if config_data["has_vis"]:
            klampt.vis.add("w", self.world)
            print("worldmodel type: ", type(self.world))
            klampt.vis.add("robby", self.robot)
            klampt.vis.visualization.resizeWindow(1920,1080)
            self.viewport = klampt.vis.getViewport()
            self.viewport.fit([0,0,-5], 25)

            klampt.vis.show()
        else:
            self.viewport = None


        if config_data["has_hud"]:
            print(config_data["has_hud"])
            print("Initializing HUD...")
            self.hud = ui.AugmentOverlayKlUI()  # Should be a place for a HUD object
        else:
            self.hud = None

        klampt.control.OmniRobotInterface.__init__(self, self.robot)
        self.state = "On"

        while klampt.vis.shown():
            asyncio.run(self.main())

    async def feedback(self, textvar):
        if self.voice:
            self.voice.announce(textvar)
        else:
            pass
        #
        # if self.hud:
        #     self.hud.subtitles.update(textvar)
        # else:
        #     pass

    async def main(self):
        # Main operating system loop.
        # Voice intake
        if self.voice:
            self.input = self.voice.voice_loop()
        else:
            self.input = "blahdy blah blah blah"

        if self.viewport:
            pass
        else:
            pass

        if self.sim:
            print(self.pcm.bones)
            self.pcm.bones = self.sim.simLoop([[0,(1,0,0),(0,0,0)] for x in self.pcm.bones])  # Needs a list of forces, derived from OSC input
        else:
            pass

        # self.hud.subtitles.update(self.input)
        # asyncio.run(self.hud.idle())
        #await self.feedback(self.input)

        #return "Running..."

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
        self.state = "Shutdown in progress"
        self.shutdown_flag = True
        self.voice.announce("Shutting down systems.")
        self.hud.async_shutdown()
        self.state = "Off"


"""
MAIN LOOP
"""
def launch_standard():
    # Want this to be platform-independent as some point
    plat = platform.platform()
    print(plat)
    if plat.startswith("Windows"):
        config_path = tk.filedialog.askopenfilename()
    else:
        config_path = None
        print("System platform error. Please update source code for this platform.")
        return FileNotFoundError

    config = configLoader(config_path)
    exo_program = ExOS(config)

if __name__ == "__main__":

    launch_standard()