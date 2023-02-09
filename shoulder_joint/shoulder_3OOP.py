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
    def __init__(self, robotmodel, sim):
        klampt.control.OmniRobotInterface.__init__(self, robotmodel)

        print("Initializing interface. . .")
        print("Initialized: ", self.initialize())
        print("Klampt Model: ", self.klamptModel())
        self.sim = sim

        self.simInitialize()

        self.controllerTestSetup()


    def simInitialize(self):
        self.addVirtualPart("arm", [0, 1, 2])
        self.pos_sensor = klampt.sim.simulation.DefaultSensorEmulator(self.sim, self)
        self.bicep = klampt.sim.simulation.DefaultActuatorEmulator(self.sim, self)


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

    def controllerTestSetup(self):
        self.klamptModel().randomizeConfig()
        self.target = self.klamptModel().getConfig()
        self.klamptModel().randomizeConfig()
        self.trajectory = RobotTrajectory(self.klamptModel(),milestones=self.target)

class ExoSim(klampt.vis.glprogram.GLRealtimeProgram):
    """
    Makes a world with a green floor and gravity. This is probably going to be the framework that I build out.
    """
    def __init__(self):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        self.world = klampt.WorldModel()
        self.sim = klampt.Simulator(self.world)
        self.sim.setGravity([0, 0, -9.8])

        #Planar2
        self.world.loadRobot("robots/planar3.rob")
        self.robot = self.world.robot(0)



        #Controllers

        print("controller")

        #Adding elements to the visualization

        klampt.vis.add("world",self.world)
        #klampt.vis.add("ball",self.ball)
        #klampt.vis.add("torso", self.torso)
        klampt.vis.add("shoulder_bot", self.robot)


        #Initializing configuration, creating a random target and setting up the move.
        """
        self.robot.randomizeConfig()
        self.robot.randomizeConfig()
        self.robot.randomizeConfig()

        self.target = self.robot.getConfig()
        self.robot.setConfig([-1,-1, -1])
        self.initial_config = self.robot.getConfig()
        self.trajectory = RobotTrajectory(self.robot, [0,1], [self.initial_config, self.target])

        klampt.vis.add("trajectory", self.trajectory)
        """


        #Controller calls
        self.XOS = klampt.control.robotinterfaceutils.RobotInterfaceCompleter(ExoBot(self.robot, self.sim))
        print(". . .")
        self.XOS.controlRate()




        #Simulator calls
        self.dt = 1.0/(self.XOS.controlRate())
        self.looper = TimedLooper(self.dt)

        #Visualization calls




        klampt.vis.run()
        while self.looper:
            try:
                self.XOS.beginStep()
                if self.XOS.status() != 'ok':
                    raise RuntimeError("Some error occured: {}".format(self.XOS.status()))
                # state queries and commands for CONTROL LOOP go here


                self.display()
                self.XOS.endStep()
            except Exception as e:
                print("Terminating on exception: ", e)
                self.looper.stop()

        self.XOS.close()
        klampt.vis.kill()


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
