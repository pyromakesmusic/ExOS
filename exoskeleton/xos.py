import time
import math


import numpy as np
import tkinter as tk
import pandas as pd
import random

import klampt
import klampt.vis # For visualization
import klampt.vis.colorize # For colorizing to easily assess robot performance
import klampt.sim.batch # For batch simulation
import klampt.sim.settle # Applies forces and lets them reach equilibrium in simulation
import klampt.sim.simulation # For simulation
import klampt.io.resource # For easy resource access
import klampt.model.subrobot # Defines the subrobot
from klampt.vis import colorize
from klampt.model import collide
import klampt.math.vectorops as kmv # This is for cross products
from klampt.model.trajectory import RobotTrajectory # Trajectory
from klampt.control.utils import TimedLooper
from klampt.plan import robotplanning, robotcspace # Configuration space
import klampt.model.create.moving_base_robot as kmcmbr
import klampt.model.create.primitives as kmcp # This is where the box is

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
    def __init__(self, id, wm, sim, ctrl, a, b):
        """
        Takes the world model and two link IDs, a robot controller, and a first and second relative link transform.
        """
        klampt.GeometricPrimitive.__init__(self)
        klampt.sim.DefaultActuatorEmulator.__init__(self, sim, ctrl)

        self.world = wm
        self.robot = self.world.robot(0)

        link_a = self.robot.link(a)  # This "link" call is being done incorrectly. Look at documentation.
        link_b = self.robot.link(b)

        self.setSegment(link_a.transform[1],link_b.transform[1])
        # Now we add some attributes that the simulated and real robot will share
        self.geometry = klampt.GeometricPrimitive()
        self.geometry.setSegment(link_a.transform[1], link_b.transform[1])

        self.muscle = None

        self.turns = 20
        self.weave_length = 1
        self.r_0 = 1
        self.l_0 = 1
        self.stiffness = 1
        self.displacement = 0
        self.pressure = 1

    def contract(self):
        """
        This should take some kind of force/pressure argument from the controller and apply it to both the simulated
        and physical robots simultaneously. Maybe more like "update"? Do I want synchronous control or asynchronous?
        Asynchronous is probably more flexible, but is going to require slightly more (but not much more) in terms of
        computing power.
        """

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
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module, and before that probably needs to be broken up
    """

    # Initialization
    def __init__(self, robotmodel,  world, sim, config_data):
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)


        self.world = world
        self.robot = robotmodel
        self.sim = sim
        self.muscles = pd.DataFrame() # I think I could add columns now, but it'll be easier to think about later

        #Loading all the muscles
        self.muscleLoader(config_data) # It's being called right here. This is important.

    def muscleLoader(self, filepath):
        """
        Given a filepath to a .csv file containing structured muscle parameters, generates a list of Muscle objects and
        assigns them to the robot model. This should generate all muscles.

        This gets called from the __init__ method.
        """
        with open(filepath["attachments"]) as attachments:
            muscleinfo_df = pd.read_csv(attachments) # This dataframe contains information on every muscle attachment
            rows = muscleinfo_df.shape[0] # This is the number of rows, so the while loop should loop "row" many times

            muscle_objects = [] #

            for x in range(rows):
                row = muscleinfo_df.iloc[x]
                link_a = int(row["link_a"])
                link_b = int(row["link_b"]) # We want these to be typed as integers when we use them to identify links.
                """
                At this point, link_a and link_b contain text labels. Let's see if we can access
                all the links from inside this method.
                """
                num_elements = self.world.numIDs()
                num_robots = self.world.numRobots()
                """
                Looks like we only have one logical robot with 31 rigid links at this point. We're going to run with that
                assumption and format the muscle_attachments accordingly, maybe I'll make a prototype one that uses 31 links
                and design the method that breaks down to subrobots next.
                """


                muscle = Muscle(row["name"], self.world, self.sim, self, link_a, link_b)
                # Should have arguments self, id, world, sim, controller, a, b
                # I now need to use the information from the row to access a particular pair of links
                muscle_objects.append(muscle)

            muscle_series = pd.Series(data=muscle_objects)
            #print("DataFrame Penultimate Shape: ", muscleinfo_df.shape)
            #print(muscle_series)
            muscleinfo_df = pd.concat([muscleinfo_df, muscle_series], axis=1)
            #print(muscleinfo_df.iloc[1])
            #print("DataFrame Final Shape: ", muscleinfo_df.shape)



    def createMuscle(self, id, a, b):
        """
        Draws the muscle lines on the robot
        """
        assert type(id) == str, "Error: Muscle ID must be string value."

        self.muscle = Muscle(self.world, self.sim, self, a, b)
        self.muscle.setSegment(a,b) # Turns the muscle into a line segment
        klampt.vis.add(id, self.muscle) # Adds the muscle to the visualization
        return self.muscle

    # Control and Kinematics
    def sensedPosition(self):
        """
        Low level actuator method.
        """
        return self.klamptModel().getDOFPosition()

    def controlRate(self):
        """
        Should be the same as the physical device.
        """
        return 100

    def setTorque(self):
        """
        Takes a list of torque inputs and sends them to controllers. Maybe one controller should control multiple actuators.
        Kind of an architectural decision.
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
        self.setPosition(self.target)
class ExoSim(klampt.sim.simulation.SimpleSimulator):
    """
    This is a class for Simulations. It will contain the substepping logic where forces are applied to simulated objects.
    """
    def __init__(self, wm, robot):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.dt = 1


    def simLoop(self, robot):
        """
        Should simulate some time step and update the world accordingly. Needs more work.
        """
        wm = self.world
        test_body = self.body(wm.rigidObject(0)) # Change this
        test_body.applyForceAtPoint([0,0,.5], [0,0,0]) # force, pworld
        self.simulate(.1)
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

        #Random stuff related to muscles
        lat = klampt.GeometricPrimitive()
        lat.setSegment(self.robot.link(4).transform[1], self.robot.link(6).transform[1])

        klampt.vis.add("latissimus", lat)
        klampt.vis.setColor("latissimus", 1, 0, 0, 1)


        self.sim = ExoSim(self.world, self.robot)
        # creation of the controller
        self.controller = ExoController(self.robot, self.world, self.sim, filepath)
        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(self.controller)


        #Simulator creation and activation comes at the very end
        self.sim.setGravity([0, 0, -9.8])

        klampt.vis.show()
        while klampt.vis.shown():
            self.sim.simLoop(self.robot)


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
        determining whether or not the option is drawn.

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
    This is tightly coupled with the GUNDAM style configuration process. Argument should include which configuration file
    to load.
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