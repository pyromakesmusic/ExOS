import klampt
import klampt.vis
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

class ExoBot():
    def __init__(self, w):
        kmcmbr.make("temp.rob",w)

class ExoSim(klampt.vis.glprogram.GLRealtimeProgram):
    """
    Makes a world with a green floor and gravity. This is probably going to be the framework that I build out.
    """
    def __init__(self):
        klampt.vis.glprogram.GLRealtimeProgram.__init__(self, "ExoTest")
        self.world = klampt.WorldModel()
        self.sim = klampt.Simulator(self.world)
        self.sim.setGravity([0, 0, -9.8])
        self.floor_geom = kmcp.box(5, 5, .01,center=[0,0,0])
        self.floor = self.world.makeTerrain("floor")
        self.floor.geometry().set(self.floor_geom)
        self.floor.appearance().setColor(0.2,0.6,0.3,1.0)

        #Items
        self.ball = kmcp.sphere(.1, center=[4,4,4], mass=1)
        self.obj = self.world.makeRigidObject("anonymous_object")

        #Robot parts
        self.torso = kmcp.box(.5, .5, 1,center=[0,0,.5], mass=200)
        #self.humerus = kmcp.box(.05, .4, .05,center=[0,.5,.5], mass=10)
        #self.forearm = kmcp.box(.05, .4, .05,center=[0,1,.5],  mass=10)

        #Planar2
        self.robot = self.world.loadRobot("robots/planar2.rob")
        print("robot ID", self.robot.getID())
        print("robot name", self.robot.getName())
        print("robot index", self.robot.index)
        print("num drivers", self.robot.numDrivers())



        #Controllers
        print("controller")

        #This section is for logically connecting the different robot parts to each other, when I figure out how to do that

        #Posers

        #Printing info

        #Adding elements to the visualization

        klampt.vis.add("world",self.world)
        klampt.vis.add("ball",self.ball)
        klampt.vis.add("torso", self.torso)
        #klampt.vis.add("humerus", self.humerus)
        #klampt.vis.add("forearm", self.forearm)
        klampt.vis.add("shoulder_bot", self.robot)




        #This section is for weird testing things I can't fully understand right now.
        self.robot.setConfig([-1,-1])


        #Run calls
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
