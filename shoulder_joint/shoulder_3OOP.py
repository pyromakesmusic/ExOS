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


"""
CLASS DEFINITIONS
"""

class ExoBot():
    def __init__(self, w):
        kmcmbr.make("temp.rob",w)

class ExoSim():
    """
    Makes a world with a green floor and gravity. This is probably going to be the framework that I build out.
    """
    def __init__(self):
        self.world = klampt.WorldModel()
        self.ulator = klampt.sim.simulation.SimpleSimulator(self.world)
        self.ulator.setGravity([0,0,-9.8])
        self.floor_geom = kmcp.box(5, 5, .01,center=[0,0,0])
        self.floor = self.world.makeTerrain("floor")
        self.floor.geometry().set(self.floor_geom)
        self.floor.appearance().setColor(0.2,0.6,0.3,1.0)
        self.ball = kmcp.sphere(.1, center=[0,0,1], mass=1)
        self.obj = self.world.makeRigidObject("anonymous_object")

        klampt.vis.add("world",self.world)
        klampt.vis.add("ball",self.ball)
        klampt.vis.run()
        while klampt.vis.shown():

            self.ulator.updateWorld()


    def insert(self, names, entity):
        klampt.vis.add(names, entity)


"""
MAIN FUNCTION CALL
"""

exo_test = ExoSim()
