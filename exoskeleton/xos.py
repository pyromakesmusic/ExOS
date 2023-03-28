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
    def __init__(self, wm, sim, ctrl, a, b):
        """
        Takes the world model and two link IDs, a robot controller, and a first and second relative link transform.
        """
        klampt.GeometricPrimitive.__init__(self)
        klampt.sim.DefaultActuatorEmulator.__init__(self, sim, ctrl)

        self.world = wm
        self.sim = sim
        self.link1T = a
        self.link2T = b
        print("Type of a: ", type(self.link1T))
        print("Type of b: ", type(self.link2T))
        self.ctrl = ctrl
        self.setSegment(self.link1T, self.link2T)

        klampt.vis.add("muscle_3", self)

        # Now we add some attributes that the simulated and real robot will share

        self.turns = 20
        self.weave_length = 1
        self.r_0 = 1
        self.l_0 = 1
        self.stiffness = 1
        self.displacement = 0
        self.pressure = 1

    def contract(self, dummy_var):
        body1 = self.sim.body(self.world.robot(0).link(self.link1T))
        body2 = self.sim.body(self.world.robot(0).link(self.link2T))

        force1 = [1,1,1]
        force2 = [-1,-1,-1]
        body1.applyForceatPoint(force1, self.link1T.transform[1])
        body2.applyForceatPoint(force2, self.link2T.transform[1])
        return



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

    def muscleLoader(self, filepath):
        """
        Given a filepath to a .csv file containing structured muscle parameters, generates a list of Muscle objects and
        assigns them to the robot model. May need to rewrite this whole thing.
        """
        return

    def createMuscle(self, id, a, b):
        """
        Draws the muscle lines on the robot
        """
        assert type(id) == str, "Error: Muscle ID must be string value."

        #muscle = klampt.GeometricPrimitive()
        """
        The below line throws an error: expecting a sequence. Wrong number of arguments I think.
        """

        self.point_a = self.world.robot(0).link(a).getTransform()[1]
        self.point_b = self.world.robot(0).link(b).getTransform()[1]

        muscle = Muscle(self.world, self.sim, self, self.point_a, self.point_b)
        muscle.setSegment(self.point_a, self.point_b) # Turns the muscle into a line segment
        klampt.vis.add(id, muscle) # Adds the muscle to the visualization
        klampt.vis.setColor(id, 0, 1, 0, 1) # Makes the muscle green so it is easy to see
        return muscle

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

        def printLinks(self):
            for link in range(self.robot.numLinks()):
                print("Link name: ", link)

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
    This is a class for Simulations.
    """
    def __init__(self, wm, robot):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.dt = 1

    def simLoop(self, robot):
        """
        Should simulate continuously for the specified number of cycles, maybe with looping or other end behavior
        """
        wm = self.world
        klampt.vis.run()
        for x in range(1,robot.numLinks()):
            body = self.body(robot.link(x))
            body.applyForceAtPoint((.1,.1,.1),(.1,.1,.1))
            self.simulate(.1)
            self.updateWorld()

class ExoGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    GUI class, contains visualization options and is usually where the simulator will be called.
    """
    def __init__(self, filepath):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        #All the world elements MUST be loaded before the Simulator is created
        self.world = klampt.WorldModel()
        self.robot = None
        self.plan = None
        self.trajectory = None
        self.actuators = None
        self.latissimus = None
        self.trapezius = None
        self.bicep = None
        self.sim = None
        self.point_a = None
        self.point_b = None
        self.controller = None
        self.XOS = None
        self.worldSetup(filepath)
        #Simulator creation and activation comes at the very end
        self.sim.setGravity([0, 0, -9.8])

# Initialization
    def worldSetup(self, filepath_dict):
        """
        Sets up the world for the simulation, and initializes the simulation.
        """
        # Simulator is initialized
        # World is added to visualization
        klampt.vis.add("world", self.world)
        self.world.loadRobot(filepath_dict["core"])
        self.robot = self.world.robot(0)
        self.muscle = None

        # Robot is added to visualization
        klampt.vis.add("X001", self.robot)

        self.sim = ExoSim(self.world, self.robot)
        # creation of the controller
        self.controller = ExoController(self.robot, self.world, self.sim, filepath_dict)
        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(self.controller)

        # This is necessary

        self.drawEdges()
        self.muscle = None
        # Gonna try to make this happen in the controller, with only visualization handled here
        latissimus = self.controller.createMuscle("latissimus", 4,6)
        trapezius = self.controller.createMuscle("trapezius", 3, 5)
        self.bicep = self.controller.createMuscle("bicep", 9, 11)
        #self.bicep.contract() #Returns an attribute error


        klampt.vis.setWindowTitle("X001  Test")
        self.viewport = klampt.vis.getViewport()
        self.viewport.fit([0,0,-5], 25)
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
        """
        wm = self.world
        for x in range(wm.numIDs()):
            wm.appearance(x).setDraw(2, True) # Makes edges visible
            wm.appearance(x).setDraw(4, True) # I believe this should make edges glow
            wm.appearance(x).setColor(2, 0, 0, 0, .5) # Makes edges black
            wm.appearance(x).setColor(3, .3, .3, .3, .3) # This makes the faces a translucent grey\
            wm.appearance(x).setColor(4, .2, 0, 1, .1) # I think this changes the glow color


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
        print("Loading muscle attachments...", fn.readline().rstrip())
        attachments = fn.readline().rstrip()
        config = {"core": core,
                      "attachments": attachments}

        return config


"""
MAIN LOOP
"""

if __name__ == "__main__":
    xo_parts = configLoader()
    print("xo_parts", xo_parts)
    exo_sim_test = ExoGUI(xo_parts)