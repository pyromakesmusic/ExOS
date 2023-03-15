import time
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



import numpy as np
import tkinter as tk
import pandas as pd
import random

import klampt
import klampt.vis # For visualization
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
LEFTARM_MATRIX = [1, 0, 0, 0, 1, 0, 0, 0, 1]
LEFTARM_ORIGIN = [1.5, 1.5, 2.5]
RIGHTARM_MATRIX =[1, 0, 0, 0, -1, 0, 0, 0, 1]
RIGHTARM_ORIGIN = [1.5, -1.5, 2.5]
LEFTLEG_MATRIX = [1, 0, 0, 0, 1, 0, 0, 0, 1]
LEFTLEG_ORIGIN = [1.2, -.5, -1.5]
RIGHTLEG_MATRIX = [1, 0, 0, 0, 1, 0, 0, 0, 1]
RIGHTLEG_ORIGIN = [-1.2, -.5, -1.5]

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
class Muscle:
    """
    Refers to exactly one McKibben muscle, with all associated attributes.
    This may end up being an interface for both an Actuator and a simulated ActuatorEmulator, running simultaneously.
    """
    def __init__(self, config_df):
        # assert type(config_dict) == dict, "Sending the wrong type of configuration."
        "Config dict must be formatted as follows: (transform_a, transform_b, label_a, label_b, force, pressure, turns, weave_length, displacement)"


        # self.link_a = config_df["link_a"]
        # self.link_b = config_df["link_b"]
        #
        # self.transform_a = config_df["transform_a"] # One 3D vector (maybe 4d?) denoting a point on a robot link
        # self.transform_b = config_df["transform_b"] # Another 3D vector (maybe 4d?) denoting a point on a robot link
        # self.label_a = config_df["label_a"] # Proximal, superior, lateral, etc. Constant.
        # self.label_b = config_df["label_b"] # Distal, inferior, medial, etc. Constant.
        # self.turns = config_df["turns"]
        # self.r_0 = config_df["r_0"]
        # self.l_0 = config_df["l_0"]
        #
        # self.force = config_df.force # Dependent variable
        # self.pressure = config_df.pressure # Independent variable
        # self.turns = config_df.turns # Constant
        # self.weave_length = config_df.weave_length # Constant?
        # self.displacement = config_df.displacement # Dependent variable
        # self.appearance = klampt.Appearance()
        # self.geometry = klampt.GeometricPrimitive(type="Segment", properties=[self.transform_a, self.transform_b])

    def updateLoop(self, pressurecommand=None):
        """
        This will be the lowest level implementation where the parameters of a muscle are changed, particularly force and pressure.
        """
        self.force = self.force


class MuscleGroup:
    def __init__(self, muscles):
        self.muscles = muscles



class ExoController(klampt.control.OmniRobotInterface):
    """
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module, and before that probably needs to be broken up
    """

    # Initialization
    def __init__(self, robotmodel,  world, config_data):
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)


        self.world = world
        self.robot = robotmodel
        self.muscles = pd.DataFrame()

        # This is where we actually load in the subRobots
        self.botAssembly(config_data)

        # Now we load in all the muscles, accessible as a dataframe
        self.muscles = self.muscleLoader(config_data["attachments"])

        print(self.muscles.columns)
        print(self.muscles.index)
        print(self.muscles.keys)


    def botAssembly(self, filepath_dict):
        """
        Given a dictionary of filepaths provided in config.txt, adds the subrobot limbs to the world and mounts them on the core.
        """

        leftarm = self.world.loadRobot(filepath_dict["leftarm"])
        leftarm.setName("leftarm")
        rightarm = self.world.loadRobot(filepath_dict["rightarm"])
        rightarm.setName("rightarm")
        leftleg = self.world.loadRobot(filepath_dict["leftleg"])
        leftleg.setName("leftleg")
        rightleg = self.world.loadRobot(filepath_dict["rightleg"])
        rightleg.setName("rightleg")

        self.robot.mount(2, leftarm, LEFTARM_MATRIX, LEFTARM_ORIGIN)
        self.robot.mount(2, rightarm, RIGHTARM_MATRIX, RIGHTARM_ORIGIN)
        self.robot.mount(4, leftleg, LEFTLEG_MATRIX, LEFTLEG_ORIGIN)
        self.robot.mount(4, rightleg, RIGHTLEG_MATRIX, RIGHTLEG_ORIGIN)


    def muscleLoader(self, filepath):
        """
        Given a filepath to a .csv file containing structured muscle parameters, generates a list of Muscle objects and
        assigns them to the robot model.
        """

        blank1 = None
        blank2 = None # I'm just using these to make a set so Python doesn't think it's a dict

        muscles = {blank1, blank2}

        with open(filepath) as fn:
            attachments = pd.read_csv(fn, sep=",", header=0, index_col="name")
        # Need to convert each row to a dictionary with one element and create a Muscle based on that
        for x in attachments.keys():
            attachdict = attachments[x].to_dict()
            muscles.add(Muscle(attachdict))
        # We use the dictionary elements to instantiate the muscles, we use the dataframe to store them and their parameters
        return muscles

    # Control and Kinematics
    def sensedPosition(self):
        return self.klamptModel().getDOFPosition()

    def controlRate(self):
        return 100

    def setTorque(self, torque):
        """
        Takes a list of torque inputs and sends them to controllers. Maybe one controller should control multiple actuators.
        Kind of an architectural decision.
        ==================================
        UPDATE: Okay so I think I'm ready to implement this method. Torque is equal to the cross product of the 3-D force
        vector (provided us by the McKibben muscle parameters and perhaps a custom method) and the distance from the fulcrum at which the distance is applied
        (constant, determined with what should be a single distance query relative to the transform - this can be optimized)
        """
        force = (2, 2, 2)
        distance = (0, 1, 0)

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

    # Function verification tests

    def diagnostics(self):
        """
        This is a diagnostic function with verbose output. May eventually be a call for more nested diagnostic subroutines.
        """
        for x in range(self.world.numRobots()):
            print(x, "Is a Robot")
            print("name: ", self.world.getName(x))

        for x in range(self.world.numIDs()):
            print(x, "is an ID")
            print(self.world.getName(x))
        print("Robot number of links: ", self.robot.numLinks())
        print("Number of IDs//: ", self.world.numIDs())

    def randomTrajectoryTest(self):
        # This populates a random trajectory for the robot to execute.
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
    This is a class for Simulations.
    """
    def __init__(self, wm):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)

        self.dt = 1


class ExoSimAV(klampt.vis.glprogram.GLRealtimeProgram):
    """
    GUI class, contains visualization options and is usually where the simulator will be called.
    """
    def __init__(self, filepath):


        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")

        #All the world elements MUST be loaded before the Simulator is created
        self.world = klampt.WorldModel()
        self.plan = None
        self.trajectory = None
        self.actuators = None

        self.worldSetup(filepath)

        #Simulator creation and activation comes at the very end
        self.sim = ExoSim(self.world)
        self.sim.setGravity([0, 0, -9.8])
        klampt.vis.run()
        self.idlefunc()

    def worldSetup(self, filepath_dict):
        """
        Sets up the world for the simulation.
        """
        klampt.vis.add("world", self.world)

        self.world.loadRobot(filepath_dict["core"])
        self.robot = self.world.robot(0)

        self.poser = klampt.robotsim.RobotPoser(self.robot)
        # The core robot has 5 links, indexed 0 through 4.


        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(
            ExoController(self.robot, self.world, filepath_dict, ))


        #This has to come after robot creation

        klampt.vis.add("X001", self.robot)


        klampt.vis.setWindowTitle("X001  Test")

        self.viewport.fit([0,0,-5],25)
        self.drawEdges()

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


    def torqueTest(self):

        print("OUTPUT FROM THE CONTROLLER:", self.XOS)
    """
    Visual Options
    """

    def drawEdges(self):
        """
        Currently needs to take the argument self.world, at some point should probably change that
        """
        wm = self.world
        for x in range(wm.numIDs()):
            print("Link", x, "geometry: ", wm.geometry(x))
            print("Link", x, "appearance: ", wm.appearance(x))
            wm.appearance(x).setDraw(2, True) # Makes edges visible
            wm.appearance(x).setDraw(4, True) # I believe this should make edges glow
            wm.appearance(x).setColor(2, 1, 1, 1, 1) # Makes edges white, something about the surface normals is not right but it's fixable
            wm.appearance(x).setColor(3, .3, .3, .3, 1) # I think this makes the specularity color red


    """
    Shutdown
    """

    def shutdown(self):
        klampt.vis.kill()


"""
FUNCTION DEFINITIONS
"""
def configLoader():
    print("Loading config.txt...")
    with open("config.txt") as fn:
        print("Loading core components...", fn.readline().rstrip())
        core = fn.readline().rstrip()
        print("Loading right arm...", fn.readline().rstrip())
        rightarm = fn.readline().rstrip()
        print("Loading left arm...", fn.readline().rstrip())
        leftarm = fn.readline().rstrip()
        print("Loading right leg...", fn.readline().rstrip())
        rightleg = fn.readline().rstrip()
        print("Loading left leg...", fn.readline().rstrip())
        leftleg = fn.readline().rstrip()
        print("Loading muscle attachments...", fn.readline().rstrip())
        attachments = fn.readline().rstrip()


        config = {"core": core,
                      "rightarm": rightarm,
                      "leftarm": leftarm,
                      "rightleg": rightleg,
                      "leftleg": leftleg,
                      "attachments": attachments}

        return config


"""
MAIN LOOP
"""

if __name__ == "__main__":
    xo_parts = configLoader()
    print("xo_parts", xo_parts)
    exo_sim_test = ExoSimAV(xo_parts)