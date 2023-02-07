from klampt import *
import klampt.vis
import klampt.model.create.primitives as kmcp
import klampt.model.create.planar_robot as kmcpr
import klampt.model.create.moving_base_robot as kmcmbr

"""
MATRIX DATA
"""
null_matrix = [[0,0,0],[0,0,0],[0,0,0]]
null_origin = [1,1,1]
null_imu = (null_matrix, null_origin)


"""
CLASS DEFINITIONS
"""
class ExoSim():
    def __init__(self):
        self.world = WorldModel()
        self.imulator = Simulator(self.world)
        self.imulator.setGravity([0,0,-1])
        klampt.vis.add("world",self.world)
        klampt.vis.run()


"""
FUNCTION DEFINITIONS
"""
KLAMPT_EXAMPLES = 'Klampt-examples'

def make_floor(world,width,depth,wall_thickness=0.005):
    """Makes a new axis-aligned "shelf" centered at the origin with
    dimensions width x depth x height. Walls have thickness wall_thickness.
    """

    #equivalent to back.transform([width,0,0,0,wall_thickness,0,0,0,height],[-width*0.5,depth*0.5,0])
    #method 3
    bottom = kmcp.box(width,depth,wall_thickness,center=[0,0,0])
    shelfgeom = Geometry3D()
    shelfgeom.setGroup()
    for i,elem in enumerate([bottom]):
        g = Geometry3D(elem)
        shelfgeom.setElement(i,g)
    shelf = world.makeTerrain("shelf")
    shelf.geometry().set(shelfgeom)
    shelf.appearance().setColor(0.2,0.6,0.3,1.0)
    return shelf

w = klampt.WorldModel()
exo_test = klampt.sim.simulation.SimpleSimulator(w)
exo_test.setGravity([0,0,-1])
shoulderbot = kmcpr.make(1, w)

# This makes a flat plane.
shelf = make_floor(w, 50,50,.01)

print("shelf ID", shelf.getID())
print("bot ID", shoulderbot.getID())

overlaps = exo_test.checkObjectOverlap()
print("overlaps", overlaps)
klampt.vis.add("world", w)
print("penetration test", exo_test.hadContact(0,1))
print(w.numRobots())
exo_test.simulate()
print("status", exo_test.getStatus())
klampt.vis.run()
exo_test.updateWorld()
klampt.vis.show()