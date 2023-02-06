import klampt
import klampt.vis
import numpy as np
import math


"""
FILEPATHS
"""
thin_cube = r"C:\Users\Pyro\Documents\Math4157\Klampt-examples\Python3\exercises\control\thincube.off"

"""
PROGRAM
"""
world = klampt.WorldModel()
floor = world.loadElement(thin_cube)
klampt.vis.add("world",world)
klampt.vis.run()