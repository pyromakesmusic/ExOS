import klampt
import klampt.vis
import klampt.model.create as kmc
import numpy as np
import math


"""
FILEPATHS
"""
thin_cube = r"C:\Users\Pyro\Documents\Math4157\Klampt-examples\Python3\exercises\control\thincube.off"
shoulder_bot = "/robots/shoulder_bot.urdf"
"""
PROGRAM
"""

"""
FUNCTIONS
"""

world = klampt.WorldModel()

world.loadElement(thin_cube)
klampt.vis.add("world_xml", "4157world_1.xml")
ball = kmc.sphere(.2)
ball2 = kmc.sphere(.2, [1,0,0])


klampt.vis.add("world",world)
klampt.vis.add("ball", ball)
klampt.vis.add("ball2", ball2)
klampt.vis.run()