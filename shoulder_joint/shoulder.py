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
ball = kmc.sphere(.2)

robot = klampt.RobotModel()

klampt.vis.add("world",world)
klampt.vis.add("ball", ball)
klampt.vis.run()