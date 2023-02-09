import time
import klampt
import klampt.vis
from klampt.model.trajectory import RobotTrajectory
from klampt.control.utils import TimedLooper
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
BONES
"""
BONE_GEOMETRY = kmcp.box(.05, .4, .05,mass=10)
FLOOR_GEOMETRY = kmcp.box(5, 5, .01,center=[0,0,0])

"""
CLASS DEFINITIONS
"""

class ExoBot(klampt.control.OmniRobotInterface):
    def __init__(self, robotmodel):
        self.interface = klampt.control.OmniRobotInterface.__init__(self, robotmodel)
        print("Initializing interface. . .")
        print("Initialized: ", self.initialize())


    def sensedPosition(self):
        return 1

    def controlRate(self):
        return 100

    def setTorque(self):
        return

    def setVelocity(self):
        return

    def moveToPosition(self):
        return



class ExoSim(klampt.vis.glprogram.GLRealtimeProgram):
    """
    Makes a world with a green floor and gravity. This is probably going to be the framework that I build out.
    """
    def __init__(self):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        self.world = klampt.WorldModel()
        self.sim = klampt.Simulator(self.world)
        self.sim.setGravity([0, 0, -9.8])
        """ 
        Makes a floor
        self.floor_geom = kmcp.box(5, 5, .01,center=[0,0,0])
        self.floor = self.world.makeTerrain("floor")
        self.floor.geometry().set(self.floor_geom)
        self.floor.appearance().setColor(0.2,0.6,0.3,1.0)
        """

        #Items
        self.ball = kmcp.sphere(.1, center=[4,4,4], mass=1)
        self.obj = self.world.makeRigidObject("anonymous_object")

        #Robot parts
        self.torso = kmcp.box(.5, .5, 1,center=[0,0,.5], mass=200)
        #self.humerus = kmcp.box(.05, .4, .05,center=[0,.5,.5], mass=10)
        #self.forearm = kmcp.box(.05, .4, .05,center=[0,1,.5],  mass=10)

        #Planar2
        self.world.loadRobot("robots/planar3.rob")
        self.robot = self.world.robot(0)
        print("robot ID", self.robot.getID())
        print("robot name", self.robot.getName())
        print("robot index", self.robot.index)
        print("num drivers", self.robot.numDrivers())



        #Controllers

        print("controller")

        #Adding elements to the visualization

        klampt.vis.add("world",self.world)
        klampt.vis.add("ball",self.ball)
        klampt.vis.add("torso", self.torso)
        klampt.vis.add("shoulder_bot", self.robot)


        #Initializing configuration, creating a random target and setting up the move.

        self.robot.randomizeConfig()
        self.robot.randomizeConfig()
        self.robot.randomizeConfig()

        self.target = self.robot.getConfig()
        self.robot.setConfig([-1,-1, -1])
        self.initial_config = self.robot.getConfig()
        self.trajectory = RobotTrajectory(self.robot, [0,1], [self.initial_config, self.target])

        klampt.vis.add("trajectory", self.trajectory)

        #Controller cals
        self.RIL = ExoBot(self.robot)
        print(". . .")
        self.RIL.controlRate()




        #Simulator calls
        self.dt = 1.0/(self.RIL.controlRate())
        self.looper = TimedLooper(self.dt)

        #Visualization calls
        klampt.vis.run()

        while self.looper:
            try:
                self.RIL.beginStep()
                if self.RIL.status() != 'ok':
                    raise RuntimeError("Some error occured: {}".format(self.RIL.status()))
                # state queries and commands for CONTROL LOOP go here

                klampt.vis.show()

                self.display()
                self.RIL.endStep()
            except Exception as e:
                print("Terminating on exception: ", e)
                self.looper.stop()

        self.RIL.close()

        #Run calls
        #klampt.vis.debug(self.robot)
        klampt.vis.run()



    def shutdown(self):
        klampt.vis.kill()

    def display(self):
        self.sim.updateWorld()
        self.world.drawGL()

        return



"""
MAIN FUNCTION CALL
"""

exo_test = ExoSim()
