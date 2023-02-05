import klampt
import klampt.vis
import numpy as np
import math

world = klampt.WorldModel()

world.readFile(r"C:\Users\Pyro\Documents\Math4157\Klampt-examples\data\simulation_test_worlds\jointtest.xml")

klampt.vis.add("world", world)
klampt.vis.show()
robot = world.robot(0)