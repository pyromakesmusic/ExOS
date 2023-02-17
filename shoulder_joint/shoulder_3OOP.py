import time
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import random

import klampt
import klampt.vis
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
class ExoEditor():
    def __init__(self):
        return

class ExoController(klampt.control.OmniRobotInterface):
    """
    This is my specialized controller subclass for the exoskeleton. Eventually this probably wants to be its own module.
    """
    def __init__(self, robotmodel, sim, world):
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)
        self.initialize()
        print("Initializing interface. . .")
        print("Initialized: ", self.initialize())
        print("Klampt Model: ", self.klamptModel())


        self.world = world
        self.sim = sim
        self.simInitialize()




    def simInitialize(self):
        self.addVirtualPart("arm", [0, 1])
        self.pos_sensor = klampt.sim.simulation.DefaultSensorEmulator(self.sim, self)
        self.bicep = klampt.sim.simulation.DefaultActuatorEmulator(self.sim, self)

        #self.randomTrajectory()


    def sensedPosition(self):
        return self.klamptModel().getDOFPosition()

    def controlRate(self):
        return 100

    def setTorque(self):
        return

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

    def idle(self):
        self.setPosition(self.target)

class ExoGUI(klampt.vis.glprogram.GLRealtimeProgram):
    """
    GUI class.
    """
    def __init__(self):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        self.world = klampt.WorldModel()
        self.sim = klampt.Simulator(self.world)
        self.sim.setGravity([0, 0, -9.8])


        #Robot Initialization
        self.world.loadRobot("robots/torso_1.rob")
        self.robot = self.world.robot(0)
        self.space = robotcspace.RobotCSpace(self.robot, collide.WorldCollider(self.world))


        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(
            ExoController(self.robot, self.sim, self.world))
        print(". . .")
        print("Control rate: ", self.XOS.controlRate())


        #Simulator parameters
        self.dt = 1.0/(self.XOS.controlRate())
        self.t = 0
        self.looper = TimedLooper(self.dt)

        #Visualization calls
        klampt.vis.add("world", self.world)
        klampt.vis.add("shoulder_bot", self.robot)


        klampt.vis.setWindowTitle("Shoulder Bot Test")

        self.viewport = klampt.vis.getViewport()
        self.randomTrajectoryTest()


        print("viewport", self.viewport)

        self.viewport.fit([0,0,0],20)
        klampt.vis.add("trajectory", self.trajectory,color=[1,1,0,1])
        self.transform = klampt.vis.add("transform", klampt.math.se3.identity())
        #self.configEdit()
        #klampt.io.resource.edit("trajectory", self.trajectory, referenceObject=self.robot)

        klampt.vis.visualization.animate("shoulder_bot", self.trajectory, speed=3, endBehavior="loop")
        klampt.vis.run()


        self.XOS.close()
        klampt.vis.kill()

    def idlefunc(self):
        self.refresh()

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
            y = [0, -.1,.2, 0]
            newconfig = np.add(x,y)
            self.trajectory.milestones.append(newconfig)
            x = newconfig
        self.trajectory.times = list(range(len(self.trajectory.milestones)))

    def shutdown(self):
        klampt.vis.kill()




"""
MAIN FUNCTION CALL
"""

exo_sim_test = ExoGUI()