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
CLASS DEFINITIONS
"""


class Muscle(klampt.GeometricPrimitive, klampt.sim.DefaultActuatorEmulator):
    """
    Refers to exactly one McKibben muscle, with all associated attributes.
    This may end up being an interface for both an Actuator and a simulated ActuatorEmulator, running simultaneously.
    """
    def __init__(self, row, wm, sim, ctrl):
        """
        Takes a dataframe row containing muscle information, a world model, a simulator, and a controller.
        """
        klampt.GeometricPrimitive.__init__(self)
        klampt.sim.DefaultActuatorEmulator.__init__(self, sim, ctrl)

        self.world = wm
        self.robot = self.world.robot(0)

        a = int(row["link_a"])
        b = int(row["link_b"])

        link_a = self.robot.link(a)
        link_b = self.robot.link(b)
        """
        The below values describe the displacement of the 
        """
        delta_a = [float(s) for s in row["transform_a"].split(",")]
        delta_b = [float(s) for s in row["transform_b"].split(",")]

        self.transform_a = kmv.add(link_a.transform[1], delta_a)
        self.transform_b = kmv.add(link_b.transform[1], delta_b)

        self.setSegment(self.transform_a, self.transform_b)
        # Now we add some attributes that the simulated and real robot will share
        self.geometry = klampt.GeometricPrimitive()
        self.geometry.setSegment(self.transform_a, self.transform_b)

        self.turns = 20 # Number of turns in the muscle fiber
        self.weave_length = 1 # at some point this should probably become a column in the attachments file
        self.r_0 = row["r_0"] # resting radius - at nominal relative pressure
        self.l_0 = row["l_0"] # resting length - at nominal relative pressure
        self.stiffness = 1 # Spring constant/variable - may change at some point
        self.displacement = 0 # This is a calculated value
        self.pressure = 1 # Should be pressure relative to external, so start at 0

    def contract(self, value):
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
        self.pressure = value
        self.displacement = kmv.distance(self.transform_a, self.transform_b) - self.l_0
        """
        Here goes...the formuoli
        """
        force = ((self.pressure * (self.weave_length)**2)/(4 * math.pi * (self.turns)**2)) * \
                (((self.weave_length)/math.sqrt(3) + self.displacement)**2 - 1)

        """
        I would not be surprised if grouping mistakes show up here, but we should display this
        for testing. We then want to apply half this force (magnitude) to each transform point in opposite directions
        derived from more vector operations on their respective transforms.
        """

        direction = kmv.sub(self.transform_a, self.transform_b)
        """
        The above should return a 3-tuple. A line between the origin and the position described by this 3-tuple should
        have the angle from a to b.
        """
        print("Force" + force)
        print("Direction" + direction)

        return

    def appearance(self):
        app = klampt.Appearance()
        app.setDraw(2, True)
        return app


class MuscleGroup:
    def __init__(self):
        pass


class ExoController(klampt.control.OmniRobotInterface):
    """
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module,
     and before that probably needs to be broken up
    """

    # Initialization
    def __init__(self, robotmodel,  world, sim, config_data):
        """
        This is intrinsically linked with a simulation. Does that make sense? Let's say it does, for now.
        """
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)

        self.world = world
        self.robot = robotmodel
        self.sim = sim
        self.muscles = pd.DataFrame() # I think I could add columns now, but it'll be easier to think about later
        self.osc_handler = osck.BlockingServer("127.0.0.1", 5005) # May eventually change to non-blocking server

        # Loading all the muscles
        self.muscles = self.muscleLoader(config_data)
        print(self.muscles)
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

                muscle = Muscle(row, self.world, self.sim, self)
                # Should have arguments self, id, world, sim, controller, a, b
                muscle_objects.append(muscle)

            muscle_series = pd.Series(data=muscle_objects, name="muscles")
            muscleinfo_df = pd.concat([muscleinfo_df, muscle_series], axis=1)

            """
            This dataframe should end with all the info in the muscle attachments CSV, plus corresponding muscle objects
            in each row.
            """
            return muscleinfo_df


    def createMuscle(self, id, a, b):
        """
        Draws the muscle lines on the robot
        """
        assert type(id) == str, "Error: Muscle ID must be string value."

        muscle = Muscle(self.world, self.sim, self, a, b)
        muscle.setSegment(a,b) # Turns the muscle into a line segment
        klampt.vis.add(id, muscle) # Adds the muscle to the visualization
        return muscle

    # Control and Kinematics
    def sensedPosition(self):
        """
        Low level actuator method.
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

    def moveToPosition(self, list_of_q):
        self.klamptModel().setConfig(list_of_q)
        return

    def setPosition(self, list_of_q):
        self.klamptModel().setConfig(list_of_q)

    def queuedTrajectory(self):
        return self.trajectory

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

    def motionPlanner(self, world):
        """
        I think this takes a world and makes a plan (trajectory without time coordinates) to reach a particular config?
        """
        self.plan = robotplanning.plan_to_config(self.world, self.robot, target=[3.14,1.4, 0])

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

    def idle(self):
        print(self.muscles.columns)


class ExoSim(klampt.sim.simulation.SimpleSimulator):
    """
    This is a class for Simulations. It will contain the substepping logic where forces are applied to simulated objects.
    """
    def __init__(self, wm, robot):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.dt = 1


    def simLoop(self, robot):
        """
        Should simulate some time step and update the world accordingly. Needs substantially more work.
        """
        wm = self.world
        #test_body = self.body(robot.link(1)) # Change this

        # test_body = self.body(wm.rigidObject(0)) # It works!!!!!!!
        # test_body.applyForceAtPoint([0,0,10], [0.5,0,0]) # this is working!!!
        """
        Now here adding a section to make sure the muscles contract in the simulation.
        """

        self.simulate(.05)
        self.updateWorld()

class ExoGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    GUI class, contains visualization options and is usually where the simulator will be called.
    """
    def __init__(self, filepath):
        """
        This is very generic on purpose.
        """
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        #All the world elements MUST be loaded before the Simulator is created

        self.world = w = klampt.io.load('WorldModel', 'worlds/test_world1.xml')# Updating this to use a particular prepared XML world file
        klampt.vis.add("world", self.world)
        self.world.loadRobot(filepath["core"])
        self.robot = self.world.robot(0)
        klampt.vis.add("X001", self.robot)
        self.drawEdges()
        klampt.vis.setWindowTitle("X001  Test")
        self.viewport = klampt.vis.getViewport()
        self.viewport.fit([0,0,-5], 25)



        self.sim = ExoSim(self.world, self.robot)
        # creation of the controller
        self.controller = ExoController(self.robot, self.world, self.sim, filepath)

        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(self.controller) # No point using this rn


        #Simulator creation and activation comes at the very end
        self.sim.setGravity([0, 0, -9.8])

        #Random stuff related to muscles
        """
        Adding more documentation since this will probably get moved and refactored.
        """
        lat = klampt.GeometricPrimitive()
        origin_delta = [0,-.5,-1]
        destination_delta = [0,-.9,1.7]

        lat_origin = kmv.add(self.robot.link(0).transform[1], origin_delta)
        lat_destination = kmv.add(self.robot.link(1).transform[1], destination_delta)
        # I'm using the klampt vector operations library here to quickly add these 3-lists as vectors.

        lat.setSegment(lat_origin, lat_destination)

        klampt.vis.add("latissimus", lat)
        klampt.vis.setColor("latissimus", 1, 0, 0, 1)


        klampt.vis.show()
        while klampt.vis.shown():
            self.sim.simLoop(self.robot)
            self.controller.idle()


    def idlefunc(self):
        pass

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


    """
    Shutdown
    """

    def shutdown(self):
        klampt.vis.kill()
"""
FUNCTION DEFINITIONS
"""
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
"""
MAIN LOOP
"""
if __name__ == "__main__":
    config = configLoader("demo_config.txt")
    exo_sim_test = ExoGUI(config)