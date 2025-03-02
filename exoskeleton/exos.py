"""
ExOS: the exoskeleton operating system for the next generation
===============================================================
This file should probably be made private at some point. It contains the code for the multithreaded, network-capable
exoskeleton framework I am designing. The goal is to be easy to iterate, easy to model and optimize, and to make use of
machine learning tools to the greatest extent possible. To that end, the following two files contain the majority of
implementation-specific details for any particular build:
- config.txt file in the config folder
- muscle_attachments.csv in the robots folder
- the .ROB file in the robots folder
- the folder we are about to create, containing data, models, libraries or whatever else that is meant to be packaged
onboard the robot in order for its proper unassisted offline operation.
"""


"""
STANDARD LIBRARIES
"""
import random
from datetime import datetime
import platform  # For detecting the platform and automatically selecting the correct launcher

import pandas as pd  # Critical, most of the data structures are pandas structures
import asyncio  # For asynchronous OSC handling
import os  # For listing files in directory

import sys
import logging
import tkinter as tk
import tkinter.filedialog as filedialog

"""
OTHER LIBRARIES
"""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
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
import klampt.model.contact  # For dealing with collisions

import klampt.plan.cspace
import klampt.plan.robotcspace
import klampt.plan.rigidobjectcspace
import klampt.plan.robotplanning

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
                  "has_hud": has_hud,
                  "has_voice": has_voice,
                  "has_persona": has_persona,
                  "voice_id": voice_id,
                  "voice_rate": voice_rate
                  }

        return config

"""
SECURITY
"""
# Function to derive a key from a password using PBKDF2
def derive_key(password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password), salt

# Function to encrypt data using AES-256
def encrypt_data(data, key, salt):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return salt + iv + encrypted_data


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
        self.model_path = config_data["model"]

        self.shutdown_flag = False
        self.state = "Initializing..."
        # Should be updated whenever something is happening to the whole system, made to be human-readable.

        self.mode = None  # Safe mode, restricted mode, etc. - None is normal
        self.network_mode = config_data["network_mode"]  # Can be master or slave
        self.dt = config_data["timestep"]

        if config_data["has_voice"]:
            self.voice = ui.VoiceAssistantUI(config_data["voice_id"], config_data["voice_rate"])
        else:
            self.voice = None

        if config_data["has_robworld"]:
            # Variable for a robot representation # Not sure if this is happening correctly
            self.pcm = ctrl.ExoController(config_data) # PCM as in powertrain control module, this is primary motor driver
            self.input = asyncio.run(self.pcm.idle(self.pcm.bones))  # async function

        if config_data["has_sim"]:  # If a simulation is defined
            self.sim = xapp.Sim(self.pcm.world, self.pcm.robot, self.pcm.controlRate())
            self.sim.enableContactFeedbackAll()
            # asyncio.run(self.sim_settings())
            self.sim.endLogging()
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
        else:
            self.viewport = None


        if config_data["has_hud"]:
            self.hud = ui.AugmentOverlayKlUI()  # Should be a place for a HUD object
        else:
            self.hud = None  # No HUD

        klampt.control.OmniRobotInterface.__init__(self, self.pcm.robot)
        if self.sim:
            asyncio.run(self.sim.configure_sim())

        self.logging = True  # This is the diagnostic output flag

        if self.logging:
            self.log_filepath = self.model_path + ("/data/" + str(datetime.now().strftime(format='%Y%m%d%H%M')) + \
                                                   r"datalog.exo")
            with open(self.log_filepath, "wb") as self.log_file:
                asyncio.run(self.pcm.idle_configuration())  # Set up the idle for the powertrain control module
                asyncio.run(vid.display_bones(self.pcm.robot))  # Sets the color of the robot links
                asyncio.run(self.startup(self.main))  # Initiates the primary idle loop for the total system
                #klampt.vis.add("Config Space", self.pcm.cspace)  # Trying to show the configuration space.
        else:
            asyncio.run(self.pcm.idle_configuration())  # Set up the idle for the powertrain control module
            asyncio.run(vid.display_bones(self.pcm.robot))  # Sets the color of the robot links
            asyncio.run(self.startup(self.main))  # Initiates the primary idle loop for the total system
            # klampt.vis.add("Config Space", self.pcm.cspace)  # Trying to show the configuration space.

    async def startup(self, self_method, *args):
        """
        Should be called with the runtime loop to be started plus some conditionals to ensure are true
        """
        self.state = "Starting up..."
        """
        Between these two state update commands should go the startup logic
        """
        # self.pcm.setCollisionFilter(world=None, op="warn")  # This makes the robot check for self-collisions and ignore commands that cause them

        self.state = "Running"

        while klampt.vis.shown():  # I ddn't know if this should be packaged somehow
            await self_method()  # Async function call
            await asyncio.sleep(2)
            # i += 1
            # asyncio.run(asyncio.sleep(1))

    async def main(self):
        # Diagnostics go here at the top
        await self.datalog()
        # await vid.display_contact_forces(self.pcm.robot, self.sim)
        if self.sim:
            # Attend to the simulation
            # await self.collision_settings()  # Should access the collision settings function and do something related to collisions every loop
            if klampt.vis.shown():
                vid.display_muscles(self.pcm.muscles)
                klampt.vis.lock()

            # Main operating system loop. Last argument of pressures_to_forces is a force multiplier.
            forces = await self.sim.pressures_to_forces(self.pcm.muscles.muscle_objects, self.pcm.pressures, 2)
            self.pcm.bones = await self.sim.simLoop(forces)  # Needs list of input values

            if klampt.vis.shown():
                klampt.vis.unlock()
                klampt.vis.update()

        else:
            pass

    async def async_error(self, error_message: None):
        print("ERROR")
        print(error_message)
        if self.voice:
            self.voice.announce("Error:")
            self.voice.announce(ui.sysvx.negatives[random.randint(0,len(ui.sysvx.negatives))])

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
        self.state = "Shutdown in progress"
        self.shutdown_flag = True
        self.voice.announce("Shutting down systems.")
        self.hud.async_shutdown()
        self.state = "Off"
        self.log_file.close()

    """
    Testing
    """
    async def trajectory_test(self):
        try:
            pass
        except KeyError:
            return "oops"
        return
    """
    Diagnostics
    """
    async def datalog(self, verbose=True):
        # A diagnostic function for printing to console or logging other relevant things at the top level.
        # print(self.pcm.muscles.shape[0])
        if self.logging:
            self.log_file.write(str(self.pcm.robot.numDrivers()).encode())

        try:
            # print("Number of robot drivers", str(self.pcm.robot.numDrivers()))
            if self.pcm.robot.numDrivers():
                for x in range(self.pcm.robot.numDrivers()):
                    # print(self.pcm.robot.driver(x).name)
                    pass
            if self.sim:
                return klampt.model.contact.sim_contact_map(self.sim)  # Returns a contact map if there's a simulation
            else:
                return None
        except SystemError:
            return "Contact map calculations failed."

"""
MAIN LOOP
"""
def launch_standard():
    # Want this to be platform-independent as some point
    plat = platform.platform()
    print("Platform: ")
    print(plat)
    print("Initializing...")
    if plat.startswith("Windows"):  # Windows default behaviour
        config_path = tk.filedialog.askopenfilename()

    else:  # Platform default error
        config_path = None
        print("System platform error. Please update source code for this platform.")
        return FileNotFoundError

    config = configLoader(config_path)
    exo_program = ExOS(config)


def launch_sim_desktop_win64():
    """
    Convenience launcher for current dev environment for Windows. Works as a simulation at the moment.
    """
    config = configLoader("config/desktopsim_testconfig2.txt")
    exo_program = ExOS(config)

if __name__ == "__main__":

    launch_sim_desktop_win64()