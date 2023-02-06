import klampt
from klampt import vis
from klampt.io import loader
from klampt.vis import GLRealtimeProgram

import time
import math
import sys

"""
CONFIG
"""

w_filepath = r"D:\#PERSONAL\#STEDWARDS\Klampt-examples\Python3\exercises\control\world1.xml"



"""
CLASS DEFINITIONS
"""

class ExoTest():
    def __init__(self, world_location):
        self.world = klampt.WorldModel()
        self.world.readFile(world_location)
        klampt.vis.show()
        time.sleep(10)

exo = ExoTest(w_filepath)

"""
world = klampt.WorldModel()
world.readFile(r"D:\#PERSONAL\#STEDWARDS\Klampt-examples\Python3\exercises\control\world1.xml")
robot = world.makeRobot("robot")
klampt.vis.show()
klampt.vis.lock()
"""