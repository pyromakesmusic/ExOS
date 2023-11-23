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

# Visualization

def colorCalc(current_pressure, max_pressure):
    if current_pressure / max_pressure < 1:
        return current_pressure / max_pressure
    else:
        return 1
def visMuscles(dataframe_row):
    # Takes a dataframe row as a namedtuple and adds muscle to visualization
    name = dataframe_row[1]  # Should be the name index
    muscle = dataframe_row[-1]  # Index of the muscle object
    greenness = ui.colorCalc(muscle.pressure, muscle.max_pressure)  # Should always be less than 1s
    klampt.vis.add(name, muscle.geometry)  # Adds the shape of the muscle - must happen
    klampt.vis.setColor(name, 0, greenness, 0, 1)  # Sets the color of the muscle (currently green
    klampt.vis.hideLabel(name)  # Hides the name of the muscle



"""
CLASS DEFINITIONS
"""

"""
Hardware
"""
class Muscle(klampt.sim.ActuatorEmulator):
    """
    Refers to exactly one McKibben muscle, with all associated attributes.
    This may end up being an interface for both an Actuator and a simulated ActuatorEmulator, running simultaneously.
    """
    def __init__(self, row, controller):
        """
        Takes a dataframe row containing muscle information, a world model, a simulator, and a controller.
        """
        klampt.sim.ActuatorEmulator.__init__(self)
        self.controller = controller
        self.a = int(row["link_a"])  # Gets index of the row of link a
        self.b = int(row["link_b"])

        self.link_a = self.controller.bones[self.a]  # Refers to the **controller's** knowledge of the link *transform*
        self.link_b = self.controller.bones[self.b]  # Might need to be updated
        """
        The below values describe the displacement of the muscle attachment from the origin of the robot link.
        """
        self.delta_a = [float(s) for s in row["transform_a"].split(",")]
        self.delta_b = [float(s) for s in row["transform_b"].split(",")]

        # This starts out fine, but may eventually need to be updated each time step according to link position
        self.transform_a = kmv.add(self.link_a[1], self.delta_a)
        self.transform_b = kmv.add(self.link_b[1], self.delta_b)

        # Now we add some attributes that the simulated and real robot will share
        self.geometry = klampt.GeometricPrimitive()
        self.geometry.setSegment(self.transform_a, self.transform_b)

        self.turns = row["turns"]  # Number of turns in the muscle fiber
        self.weave_length = row["weave_length"]  # weave length - should be shorter than l_0
        self.max_pressure = row["max_pressure"]  # want this to autoscale for now, eventually static
        self.r_0 = row["r_0"]  # resting radius - at nominal relative pressure
        self.l_0 = row["l_0"]  # resting length - at nominal relative pressure
        self.length = self.l_0  # For calculation convenience. self.length should change eache time step
        self.displacement = 0  # This is a calculated value; should initialize at 0
        self.pressure = 0  # Should be pressure relative to external, so initialize at 0 - need units eventually

    def update(self, pressure): # Should call every loop?
        """
        ================
        UPDATE 10.2.2023: A muscle is a spring with variable stiffness.

        Should apply two forces at points determined by self.transform_a and self.transform_b, moderated by the
        McKibben muscle formula.

        We want to calculate
        F: the force applied by the muscle.
        To do this we will need:
        p: relative pressure of the air chamber
        b: the muscle fiber weave length
        n: number of turns in the muscle fiber
        x: the displacement. This will probably take the most work to calculate.
        """
        # Muscle transforms must update based on new link positions //// maybe not with applyForceAtLocalPoint()
        self.link_a = self.controller.bones[self.a]
        self.link_b = self.controller.bones[self.b]

        self.transform_a = kmv.add(self.link_a[1], self.delta_a)  # Adds link transform to muscle delta
        self.transform_b = kmv.add(self.link_b[1], self.delta_b)

        self.geometry.setSegment(self.transform_a, self.transform_b)  # Should be updating the transform

        self.pressure = pressure  # Updates muscle pressure

        self.length = kmv.distance(self.transform_a, self.transform_b)
        self.displacement = self.length - self.l_0  # Calculates displacement based on new length

        # Muscle formula
        force = ((self.pressure * (self.weave_length)**2)/(4 * math.pi * (self.turns)**2)) * \
                (((self.weave_length)/math.sqrt(3) + self.displacement)**2 - 1)

        # Calculating a 3-tuple that gives a direction
        direction_a = kmv.sub(self.transform_a, self.transform_b)
        direction_b = kmv.mul(direction_a, -1) # Should just be the reverse of direction_a

        # Calculating unit vectors by dividing 3-tuple by its length
        unit_a = kmv.div(direction_a, self.length)
        unit_b = kmv.mul(direction_b, self.length)  # Redundant but I'm including this to make it easier to read for now

        # Combining unit vectors and force magnitude to give a force vector
        force_a = kmv.mul(kmv.mul(unit_a, force), 5)  # Half (.5) because of Newton's Third Law,
        force_b = kmv.mul(kmv.mul(unit_b, force), 5)

        triplet_a = [self.b, force_a, self.transform_b]  # Should be integer, 3-tuple, transform
        triplet_b = [self.a, force_b, self.transform_a]
        """
        These triplets are what is required to simulate the effect of the muscle contraction. Also, at some point I want
        to change the muscle color based on the pressure input.
        """
        return triplet_a, triplet_b

    def pressure_autoscale(self):
        if self.pressure > self.max_pressure:  # autoscaling algorithm
            self.max_pressure = self.pressure

    def appearance(self):
        app = klampt.Appearance()
        app.setDraw(2, True)
        app.setColor(0, 1, 0, 1)
        return app

"""
Controllers
"""
class ExOS(klampt.control.OmniRobotInterface):
    """
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module,
     and before that probably needs to be broken up
     UPDATE:
     Seems like this is very much like a high level controller. Maybe change the class name to avoid confusing documentation
     and scope.
    """

    # Initialization
    def __init__(self, config_data):
        """
        Initializes the controller. Should work on a physical or simulated robot equivalently or simultaneously.
        """
        print(config_data)
        self.shutdown_flag = False

        self.input = None
        self.assistant = ui.VoiceAssistantUI(1, 150)
        # self.assistant.announce("Initializing systems.")
        # Testing the voice assistant

        self.world = klampt.io.load('WorldModel', config_data["world_path"])  # Loads the world
        self.world.loadRobot(config_data["core"])
        self.robot = self.world.robot(0)
        klampt.control.OmniRobotInterface.__init__(self, self.robot)



        self.dt = config_data["timestep"]
        self.osc_handler = osck.AsyncServer(config_data["address"], config_data["port"])
        self.oscMapper()

        # Creating a series of link transforms, I need to check if this gets updated automatically
        self.bones = pd.Series([self.robot.link(x).getTransform() for x in range(self.robot.numLinks())])

        # Loading all the muscles
        self.muscles = self.muscleLoader(config_data)

        # Setting initial muscle pressure to zero
        self.pressures = [0 for muscle in range(len(self.muscles))]


    def muscleLoader(self, config_df):
        """
        Given a dataframe with an ["attachments"] column containing a path
        to a .csv file detailing structured muscle parameters, generates a list of Muscle objects and
        assigns them to the robot model. This should generate all muscles.
        """
        with open(config_df["attachments"]) as attachments:
            muscleinfo_df = pd.read_csv(attachments, sep=";")  # This dataframe contains info on every muscle attachment
            rows = muscleinfo_df.shape[0]  # This is the number of rows, so the while loop should loop "row" many times

            muscle_objects = []  # Placeholder list, made to be empty and populated with all muscle objects.

            for x in range(rows):
                row = muscleinfo_df.iloc[x] # Locates the muscle information in the dataframe
                muscle = ctrl.Muscle(row, self) # Calls the muscle class constructor
                muscle_objects.append(muscle) # Adds the muscle to the list

            muscle_series = pd.Series(data=muscle_objects, name="muscle_objects")
            muscleinfo_df = pd.concat([muscleinfo_df, muscle_series], axis=1)

            """
            This dataframe should end with all the info in the muscle attachments CSV, plus corresponding muscle objects
            in each row.
            """
            return muscleinfo_df

    # Control and Kinematics

    def oscMapper(self):
        """
        Sets up the OSC control inputs.
        """
        self.osc_handler.map("/pressures", self.setPressures)
        return
    def sensedPosition(self):
        """
        Returns the list of link transforms.
        """
        return self.bones

    def setPressures(self, *args):  # Constructed to work with an arbitrary number of values
        args = list(args[2:-1])  # Removing unnecessary elements, we are getting four values now
        self.pressures = [pressure for pressure in args]
        return

    def validateInput(self, stringvar):
        if stringvar == None:
            return ""
        else:
            return stringvar

    def controlRate(self):
        """
        Should be the same as the physical device, Reaktor control rate, simulation timestep
        """
        return self.dt

    def beginIdle(self):
        """
        Used for loops.
        """
        self.shutdown_flag = False
        while not self.shutdown_flag:
            self.idle()

    def idle(self, bones_transforms):
        """
        bones_transforms: A list of link locations
        """
        self.input = self.validateInput(self.assistant.voice_loop())  # Runs the voice assistant at idle to get input
        self.bones = bones_transforms  # Not working quite right, might need rotation
        force_list = []  # Makes a new empty list... of tuples? Needs link number, force, and transform
        i = 0
        for muscle in self.muscles.muscle_objects:
            triplet_a, triplet_b = muscle.update(self.pressures[i])  # Updates muscles w/ OSC argument
            force_list.append(triplet_a)
            force_list.append(triplet_b)
            i += 1
        return pd.Series(force_list)

    # Test Methods

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
Interfaces
"""
class ExoGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    desktopGUI class, contains visualization options and is usually where the simulator will be called.
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


        # creation of the controller
        self.controller = ExOS(config)
        klampt.vis.add("world", self.controller.world)
        klampt.vis.add("X001", self.controller.robot)
        self.assistant = self.controller.assistant

        # creation of the simulation
        self.sim = ExoSim(self.controller.world, self.controller.robot, config["timestep"])


        # Adds the HUD - must come after controller and assistant
        if True:
            self.hud = ui.AugmentOverlayKlUI(config)
        else:
            self.hud = None

        # Adds the muscles to the visualization

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
    exo_test = ui.AugmentOverlayKlUI(config)


if __name__ == "__main__":
    initialize("test_config2.txt")