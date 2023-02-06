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

w_filepath = r"D:\#PERSONAL\#STEDWARDS\Math4157\shoulder_joint\block.xml"
r_filepath = r"\shoulder_joint\robot\shoulder_bot.urdf"


"""
CLASS DEFINITIONS
"""

class ExoTest():
    def __init__(self, world_location):
        self.world = klampt.WorldModel()
#        self.world.readFile(world_location)

        klampt.vis.run()
#        klampt.vis.add("world", self.world)

exo = ExoTest(w_filepath)


