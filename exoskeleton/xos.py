"""
STANDARD LIBRARIES
"""

import time
import math
import numpy as np
import tkinter as tk
import pandas as pd
import random

"""
KLAMPT IMPORTS
"""

import klampt
import klampt.vis # For visualization
import klampt.vis.colorize # For colorizing to easily assess robot performance
import klampt.sim.batch # For batch simulation
import klampt.sim.settle # Applies forces and lets them reach equilibrium in simulation
import klampt.sim.simulation # For simulation
import klampt.io.resource # For easy resource access
import klampt.model.subrobot # Defines the subrobot
from klampt.model import collide
import klampt.math.vectorops as kmv # This is for cross products
from klampt.model.trajectory import RobotTrajectory # Trajectory
from klampt.plan import robotplanning, robotcspace # Configuration space
import klampt.model.create.primitives as kmcp # This is where the box is

"""
CUSTOM LIBRARIES
"""
import pyonics.submodules.network.osc_toolkit as osck

"""
PANDAS CONFIG
"""
pd.options.display.width = 0
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

"""
MATRIX DATA
"""
NULL_MATRIX = [1, 0, 0, 0, 1, 0, 0, 0, 1]
NULL_ORIGIN = [0, 0, 0]
NULL_TRANSFORM = (NULL_MATRIX, NULL_ORIGIN)


"""
LIMB ATTACHMENT POINTS
"""

IDENTITY_MATRIX = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
X_MATRIX = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

"""
PARAMETER DICTIONARIES
"""
TEST_MUSCLE = {"name": None,
               "link_a": None,
               "link_b": None,
               "transform_a" : 0,
               "transform_b": 0,
               "label_a": "proximal",
               "label_b": "distal",
               "force": 0,
               "pressure": 0,
               "weave_length": 1,
               "turns": 5,
               "displacement": 0,
               "geometry": None}

"""
GEOMETRIES
"""
BONE_GEOMETRY = kmcp.box(.05, .4, .05, mass=10)
FLOOR_GEOMETRY = kmcp.box(5, 5, .01, center=[0, 0, 0])


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
        core = fn.readline().rstrip()
        print("Loading muscle attachments...", fn.readline().rstrip())
        attachments = fn.readline().rstrip()
        config = {"core": core,
                      "attachments": attachments}

        return config

# Visualization
def visMuscles(dataframe_row):
    # Takes a dataframe row as a namedtuple and adds muscle to visualization
    name = dataframe_row[1] # Should be the name index
    muscle = dataframe_row[11] # Should be index of the muscle object
    klampt.vis.add(name, muscle.geometry)
    klampt.vis.setColor(name, 1, 0, 0, 1)

"""
CLASS DEFINITIONS
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


        self.controller = controller # Big question mark goes here
        self.robot = self.controller.robot
        a = int(row["link_a"])
        b = int(row["link_b"])

        self.link_a = self.robot.link(a)
        self.link_b = self.robot.link(b)
        """
        The below values describe the displacement of the muscle attachment from the origin of the robot link.
        """
        self.delta_a = [float(s) for s in row["transform_a"].split(",")]
        self.delta_b = [float(s) for s in row["transform_b"].split(",")]

        # This starts out fine, but may eventually need to be updated each time step according to link position
        self.transform_a = kmv.add(self.link_a.transform[1], self.delta_a)
        self.transform_b = kmv.add(self.link_b.transform[1], self.delta_b)

        # Now we add some attributes that the simulated and real robot will share
        self.geometry = klampt.GeometricPrimitive()
        self.geometry.setSegment(self.transform_a, self.transform_b)

        self.turns = 20 # Number of turns in the muscle fiber
        self.weave_length = 1 # at some point this should probably become a column in the attachments file
        self.r_0 = row["r_0"] # resting radius - at nominal relative pressure
        self.l_0 = row["l_0"] # resting length - at nominal relative pressure
        self.length = self.l_0 # For calculation convenience
        self.stiffness = 1 # Spring constant/variable - may change at some point
        self.displacement = 0 # This is a calculated value
        self.pressure = 1 # Should be pressure relative to external, so start at 0

    def contract(self, pressure): # Should call every loop?
        """
        This should take some kind of force/pressure argument from the controller and apply it to both the simulated
        and physical robots simultaneously. Maybe more like "update"? Do I want synchronous control or asynchronous?
        Asynchronous is probably more flexible, but is going to require slightly more (but not much more) in terms of
        computing power.
        ================
        UPDATE 10.2.2023:

        More commentary. A muscle is a spring with variable stiffness. So, the simplest implementation should just be
        a single value that informs the pressure/stiffness.

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
        # Muscle transforms must update based on new link positions
        self.transform_a = self.transform_a
        self.transform_b = self.transform_b


        self.pressure = pressure
        self.length = kmv.distance(self.transform_a, self.transform_b)
        self.displacement = self.length - self.l_0

        # Muscle formula
        force = ((self.pressure * (self.weave_length)**2)/(4 * math.pi * (self.turns)**2)) * \
                (((self.weave_length)/math.sqrt(3) + self.displacement)**2 - 1)

        # Calculating a 3-tuple that gives a direction
        direction_a = kmv.sub(self.transform_a, self.transform_b)
        direction_b = kmv.mul(direction_a, -1)

        # Calculating unit vectors by dividing 3-tuple by its length
        unit_a = kmv.div(direction_a, self.length)
        unit_b = kmv.mul(unit_a, -1) # Redundant but I'm including this to make it easier to read for now

        # Combining unit vectors and force magnitude to give a force vector
        force_a = kmv.mul(kmv.mul(unit_a, force), 5000) # Half because of Newton's Third Law, changing to 500 for testing
        force_b = kmv.mul(kmv.mul(unit_b, force), 5000)

        forces = (force_a, force_b)
        """
        The above code should now be applying forces. Think I also need to get the transforms to apply them to.
        """

        return forces

    def appearance(self):
        app = klampt.Appearance()
        app.setDraw(2, True)
        app.setColor(1, 0, 0, 1)
        return app


class MuscleGroup:
    """
    This is for convenience, for later. Maybe making multiple muscle groups contract together makes sense?
    """
    def __init__(self):
        pass


class ExoController(klampt.control.OmniRobotInterface):
    """
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module,
     and before that probably needs to be broken up
    """

    # Initialization
    def __init__(self, robotmodel,  world, config_data):
        """
        This is intrinsically linked with a simulation. Does that make sense? Let's say it does, for now.
        """
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)

        self.world = world
        self.robot = robotmodel
        self.osc_handler = osck.BlockingServer("127.0.0.1", 5005) # May eventually change to non-blocking server

        # Creating a series of link transforms, I need to check if this gets updated automatically
        self.bones = pd.Series([self.robot.link(x).getTransform() for x in range(self.robot.numLinks())])
        print(self.bones)

        # Loading all the muscles
        self.muscles = self.muscleLoader(config_data)
        """
        This is called in the controller initialization, so should be happening in every Simulation and GUI loop.
        """

    def muscleLoader(self, config_df):
        """
        Given a dataframe with an ["attachments"] column containing a path
        to a .csv file detailing structured muscle parameters, generates a list of Muscle objects and
        assigns them to the robot model. This should generate all muscles.

        This gets called from the __init__ method.
        """
        with open(config_df["attachments"]) as attachments:
            muscleinfo_df = pd.read_csv(attachments, sep=";")  # This dataframe contains info on every muscle attachment
            rows = muscleinfo_df.shape[0]  # This is the number of rows, so the while loop should loop "row" many times

            muscle_objects = []  # Placeholder list, made to be empty and populated with all muscle objects.

            for x in range(rows):
                row = muscleinfo_df.iloc[x]

                muscle = Muscle(row, self)
                muscle_objects.append(muscle)

            muscle_series = pd.Series(data=muscle_objects, name="muscle_objects")
            muscleinfo_df = pd.concat([muscleinfo_df, muscle_series], axis=1)

            """
            This dataframe should end with all the info in the muscle attachments CSV, plus corresponding muscle objects
            in each row.
            """
            return muscleinfo_df

    # Control and Kinematics
    def sensedPosition(self):
        """
        Low level sensor method.
        """
        return self.klamptModel().getDOFPosition()

    def controlRate(self):
        """
        Should be the same as the physical device, Reaktor control rate, simulation timestep
        """
        return 20

    def setTorque(self):
        """
        Takes a list of torque inputs and sends them to controller.
        ==================================
        UPDATE: Okay so I think I'm ready to implement this method. Torque is equal to the cross product of the 3-D force
        vector (provided us by the McKibben muscle parameters and perhaps a custom method) and the distance from the fulcrum at which the distance is applied
        (constant, determined with what should be a single distance query relative to the transform - this can be optimized)
        """
        force = [2, 2, 2]
        distance = [0, 1, 0]
        torque = klampt.math.vectorops.cross(force, distance)
        return torque

    def setVelocity(self):
        return

    def moveToPosition(self):
        return

    def setPosition(self):
        return

    def queuedTrajectory(self):
        return

    def beginIdle(self):
        """
        Used for loops.
        """
        self.shutdown_flag = False

        while self.shutdown_flag == False:
            self.idle()

    # Editing functions
    def geomEdit(self,n, fn):
        """
        Opens a geometry editor for the input arguments.
        """
        klampt.io.resource.edit(n, fn, editor="visual", world=self.world)

    def configEdit(self):
        """
        Opens an editor for the configuration of the stated variables.
        """
        klampt.io.resource.edit("trajectory", self.trajectory, editor="visual", world=self.world, referenceObject=self.robot)

    """
    SYSTEM DIAGNOSTICS
    This section is for confirming baseline function of the exoskeleton and troubleshooting fatal errors.
    """

    """
    SYSTEM BENCHMARKING
    This section is for measurement of system functions and data collection for further optimization.
    """

    def randomTrajectoryTest(self):
        """
        Creates a random trajectory for the robot to execute.
        """
        self.trajectory = klampt.model.trajectory.RobotTrajectory(self.robot)
        print("trajectory", self.trajectory)
        x = self.robot.getConfig()
        for i in range(10):
            y = [0, 0, 0, 0, 0, .5, 0]
            newconfig = np.add(x,y)
            self.trajectory.milestones.append(newconfig)
            x = newconfig
        self.trajectory.times = list(range(len(self.trajectory.milestones)))

    def idle(self, command_list):
        """
        command_list: Should come from OSC signal but may be something else for testing
        """
        self.bones = self.bones.apply(klampt.math.se3.apply) # Change this, want to apply transforms to each

        force_list = [] # Makes a new empty list
        for muscle in self.muscles.muscle_objects:
            forces = muscle.contract(100) # This is probably important, should eventually contract w OSC argument
            force_list.append(forces)

        return force_list


class ExoSim(klampt.sim.simulation.SimpleSimulator):
    """
    This is a class for Simulations. It will contain the substepping logic where forces are applied to simulated objects.
    """
    def __init__(self, wm, robot):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.dt = 1


    def simLoop(self, robot, force_list):
        """
        robot: A RobotModel.
        force_list: Not sure what data structure, maybe a dataframe? name of muscle as index, with force and transform

        Should possibly return a list of new transforms to be used for calculating stuff in the next time step.

        """
        wm = self.world
        # test_body = self.body(robot.link(1)) # Change this

        # test_body = self.body(wm.rigidObject(0)) # It works!!!!!!!
        # test_body.applyForceAtPoint([0,0,10], [0.5,0,0]) # this is working!!!
        link_transforms_start = [robot.link(x).getTransform() for x in range(robot.numLinks())]
        """
        Now here adding a section to make sure the muscles contract in the simulation.
        """
        self.simulate(.05)
        self.updateWorld()

        """
        Maybe here is where we have to get the updated link transforms and return them as "sensor" feedback.
        """
        link_transforms_end = [robot.link(x).getTransform() for x in range(robot.numLinks())]

        link_transforms_diff = [klampt.math.se3.error(link_transforms_start[x], link_transforms_end[x])
                                for x in range(len(link_transforms_start))] # Takes the Lie derivative from start -> end

        return link_transforms_diff # I don't even know if we need to use this, depends on if we pass by ref or var

class ExoGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    GUI class, contains visualization options and is usually where the simulator will be called.
    """
    def __init__(self, filepath):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        #All the world elements MUST be loaded before the Simulator is created

        self.world = w = klampt.io.load('WorldModel', 'worlds/test_world1.xml')# Updating this to use a particular prepared XML world file
        klampt.vis.add("world", self.world)
        self.world.loadRobot(filepath["core"])
        self.robot = self.world.robot(0)
        klampt.vis.add("X001", self.robot)
        self.drawEdges()
        klampt.vis.setWindowTitle("X001  Test")
        klampt.vis.setBackgroundColor(0,.75,1,1) # Makes background teal
        self.viewport = klampt.vis.getViewport()
        self.viewport.fit([0,0,-5], 25)


        # creation of the simulation
        self.sim = ExoSim(self.world, self.robot)
        # creation of the controller
        self.controller = ExoController(self.robot, self.world, filepath)
        self.commands = [] # List of commands to the muscles, this might need to contain stuff here - we will see

        # Adds the muscles to the visualization
        self.drawMuscles()

        #Simulator creation and activation comes at the very end
        self.sim.setGravity([0, 0, -9.8])



        klampt.vis.show()
        while klampt.vis.shown():
            # Initiates the visualization idle loop
            self.idlefunc(self.commands)


    def idlefunc(self, commands):
        """
        Idle function for the GUI that sends commands to the controller, gets forces from it, and sends to the sim.
        """
        forces = self.controller.idle(self.commands) # Commands should be a list of pressure values or their analogues
        self.sim.simLoop(self.robot, forces) # Probably needs to return new transforms or "sensed positions" to ctrl
        return

    """
    Test Methods
    """
    def animationTest(self):
        """
        Animates the native trajectory.
        """
        klampt.vis.visualization.animate("X001", self.trajectory, speed=3, endBehavior="loop")
        klampt.vis.run()
        STOP_FLAG = False
        while STOP_FLAG == False:
            self.idlefunc()

        self.XOS.close()
        klampt.vis.kill()

    """
    Visual Options
    """
    def drawEdges(self):
        """
        Changes some drawing options for link geometry
        In the setDraw function, the first argument is an integer denoting vertices, edges. etc. The second is a Boolean
        determining regardless of whether the option is drawn.

        setColor function takes an int and RGBA float values.
        """
        wm = self.world
        for x in range(wm.numIDs()):
            wm.appearance(x).setDraw(2, True) # Makes edges visible
            wm.appearance(x).setDraw(4, True) # I believe this should make edges glow
            wm.appearance(x).setColor(2, 0, 0, 0, .5) # Makes edges black
            wm.appearance(x).setColor(4, 0, 0, .9, .4) # This makes the faces a translucent grey\
            wm.appearance(x).setColor(4, 0, 0, 1, .5) # I think this changes the glow color

    def drawMuscles(self):
        """
        This function takes all the muscles from the controller dataframe and draws them in the visualization
        """
        muscle_df = self.controller.muscles
        for row in muscle_df.itertuples():
            visMuscles(row)


    """
    Shutdown
    """

    def shutdown(self):
        klampt.vis.kill()

"""
MAIN LOOP
"""
if __name__ == "__main__":
    config = configLoader("demo_config.txt")
    exo_sim_test = ExoGUI(config)