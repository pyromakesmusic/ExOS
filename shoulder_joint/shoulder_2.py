from klampt import *
import klampt.vis
import klampt.model.create.primitives as kmcp
import klampt.model.create.planar_robot as kmcpr
import klampt.model.create.moving_base_robot as kmcmbr
"""
FUNCTION DEFINITIONS
"""
KLAMPT_EXAMPLES = 'Klampt-examples'

def make_shelf(world,width,depth,height,wall_thickness=0.005):
    """Makes a new axis-aligned "shelf" centered at the origin with
    dimensions width x depth x height. Walls have thickness wall_thickness.
    """
    left = Geometry3D()
    right = Geometry3D()
    back = Geometry3D()
    bottom = Geometry3D()
    top = Geometry3D()
    #method 1
    left.loadFile("terrains/block.off")
    left.transform([wall_thickness,0,0,0,depth,0,0,0,height],[-width*0.5,-depth*0.5,0])
    right.loadFile("terrains/block.off")
    right.transform([wall_thickness,0,0,0,depth,0,0,0,height],[width*0.5,-depth*0.5,0])
    #method 2
    back.loadFile("terrains/block.off")
    back.scale(width,wall_thickness,height)
    back.translate([-width*0.5,depth*0.5,0])
    #equivalent to back.transform([width,0,0,0,wall_thickness,0,0,0,height],[-width*0.5,depth*0.5,0])
    #method 3
    bottom = kmcp.box(width,depth,wall_thickness,center=[0,0,0])
    top = kmcp.box(width,depth,wall_thickness,center=[0,0,height-wall_thickness*0.5])
    shelfgeom = Geometry3D()
    shelfgeom.setGroup()
    for i,elem in enumerate([left,right,back,bottom,top]):
        g = Geometry3D(elem)
        shelfgeom.setElement(i,g)
    shelf = world.makeTerrain("shelf")
    shelf.geometry().set(shelfgeom)
    shelf.appearance().setColor(0.2,0.6,0.3,1.0)
    return shelf

w = klampt.WorldModel()
robot = kmcpr.make(1, w)

print(robot.numLinks())
shelf = make_shelf(w, 1,1,1)

klampt.vis.add("world", w)
klampt.vis.run()
