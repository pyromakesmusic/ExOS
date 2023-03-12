import time
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



import numpy as np
import random

import klampt
import klampt.vis
import klampt.sim.batch
import klampt.sim.settle
import klampt.sim.simulation
import klampt.io.resource
from klampt.vis import colorize
from klampt.model import collide
from klampt.model.trajectory import RobotTrajectory
from klampt.control.utils import TimedLooper
from klampt.plan import robotplanning, robotcspace
import klampt.model.create.moving_base_robot as kmcmbr
import klampt.model.create.primitives as kmcp


"""
MATRIX DATA
"""
null_matrix = [[0,0,0],[0,0,0],[0,0,0]]
null_origin = [1,1,1]
null_imu = (null_matrix, null_origin)


x_matrix = [[1,0,0],[0,0,0],[0,0,0]]
"""
GEOMETRIES
"""
BONE_GEOMETRY = kmcp.box(.05, .4, .05,mass=10)
FLOOR_GEOMETRY = kmcp.box(5, 5, .01,center=[0,0,0])

"""
CLASS DEFINITIONS
"""
class Muscle:
    """
    Refers to exactly one McKibben muscle.
    """
    def __init__(self, config_dict):
        "Config dict must be formatted as follows: (transform_a, transform_b, label_a, label_b, force, pressure, turns, weave_length, displacement)"
        self.transform_a = config_dict["transform_a"]
        self.transform_b = config_dict["transform_b"]
        self.label_a = config_dict["label_a"]
        self.label_b = config_dict["label_b"]
        self.force = config_dict["force"]
        self.pressure = config_dict["pressure"]
        self.turns = config_dict["turns"]
        self.weave_length = config_dict["weave_length"]
        self.displacement = config_dict["displacement"]



class MuscleGroup:
    def __init__(self, muscles):
        self.muscles = muscles
class ExoController(klampt.control.OmniRobotInterface):
    """
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module.
    """
    def __init__(self, robotmodel,  world, filepath_dict):
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)
        print("Initializing interface. . .")
        print("Klampt Model: ", self.klamptModel())


        self.world = world
        self.sim = None
        self.actuators = {"bicep"}
        self.rightarm = None
        self.leftarm = None
        self.rightleg = None
        self.leftleg = None
        self.botAssembly(filepath_dict)

    def botAssembly(self, filepath_dict):
        """
        Given a dictionary of filepaths provided in config.txt, adds the subrobot limbs to the world and mounts them on the core.
        """
        self.rightarm = self.world.loadRobot(filepath_dict["rightarm"])
        self.leftarm = self.world.loadRobot(filepath_dict["leftarm"])
        self.rightleg = self.world.loadRobot(filepath_dict["rightleg"])
        self.leftleg = self.world.loadRobot(filepath_dict["leftleg"])

    def sensedPosition(self):
        return self.klamptModel().getDOFPosition()

    def controlRate(self):
        return 100

    def setTorque(self, torque):
        """
        Takes a list of torque inputs and sends them to controllers. Maybe one controller should control multiple actuators.
        Kind of an architectural decision.
        """

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
        self.shutdown_flag = False

        while self.shutdown_flag == False:
            self.idle()

    @classmethod
    def getActuators(self):
        return self.actuators

    def idle(self):
        self.setPosition(self.target)

class ExoSimGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    GUI class.
    """
    def __init__(self, filepath):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")

        #All the world elements MUST be loaded before the Simulator is created
        self.world = klampt.WorldModel()


        #Simulator parameters


        self.plan = None
        self.trajectory = None
        self.actuators = None

        self.worldSetup(filepath)





        #Simulator creation and activation comes at the very end
        self.sim = klampt.Simulator(self.world)
        self.sim.setGravity([0, 0, -9.8])
        klampt.vis.run()
        self.idlefunc()

    def worldSetup(self, filepath_dict):
        klampt.vis.add("world", self.world)
        self.world.loadRobot(filepath_dict["core"])
        self.robot = self.world.robot(0)
        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(
            ExoController(self.robot, self.world, filepath_dict))


        print(". . .")
        print("Control rate: ", self.XOS.controlRate())

        #This has to come after robot creation
        klampt.vis.add("X001", self.robot)


        klampt.vis.setWindowTitle("X001  Test")

        self.viewport = klampt.vis.getViewport()
        print("viewport", self.viewport)

        self.viewport.fit([0,0,0],25)

    def idlefunc(self):
        pass

    def geomEdit(self,n, fn):
        klampt.io.resource.edit(n, fn, editor="visual", world=self.world)

    def configEdit(self):
        klampt.io.resource.edit("trajectory", self.trajectory, editor="visual", world=self.world, referenceObject=self.robot)

    def motionPlanner(self, world):
        self.plan = robotplanning.plan_to_config(self.world, self.robot, target=[3.14,1.4, 0])
    def randomTrajectoryTest(self):
        self.trajectory = klampt.model.trajectory.RobotTrajectory(self.robot)
        print("trajectory", self.trajectory)
        x = self.robot.getConfig()
        for i in range(10):
            y = [0, 0, 0, 0, 0, .5, 0]
            newconfig = np.add(x,y)
            self.trajectory.milestones.append(newconfig)
            x = newconfig
        self.trajectory.times = list(range(len(self.trajectory.milestones)))

    def actuatorTest(self):
        print("...placeholder...")


    def animationTest(self):
        #Visualization calls


        klampt.vis.visualization.animate("X001", self.trajectory, speed=3, endBehavior="loop")
        klampt.vis.run()
        STOP_FLAG = False
        while STOP_FLAG == False:
            self.idlefunc()

        self.XOS.close()
        klampt.vis.kill()


    def torqueTest(self):

        print("OUTPUT FROM THE CONTROLLER:", self.XOS)

    def shutdown(self):
        klampt.vis.kill()


"""
FUNCTION DEFINITIONS
"""
def configLoader():
    print("Loading config.txt...")
    with open("config.txt") as fn:
        print("Loading...", fn.readline().rstrip())
        core = fn.readline().rstrip()
        print("Loading...", fn.readline().rstrip())
        rightarm = fn.readline().rstrip()
        print("Loading...", fn.readline().rstrip())
        leftarm = fn.readline().rstrip()
        print("Loading...", fn.readline().rstrip())
        rightleg = fn.readline().rstrip()
        print("Loading...", fn.readline().rstrip())
        leftleg = fn.readline().rstrip()

        components = {"core": core,
                      "rightarm": rightarm,
                      "leftarm": leftarm,
                      "rightleg": rightleg,
                      "leftleg": leftleg}
        return components


"""
MAIN LOOP
"""

if __name__ == "__main__":
    xo_parts = configLoader()
    print("xo_parts", xo_parts)
    exo_sim_test = ExoSimGUI(xo_parts)