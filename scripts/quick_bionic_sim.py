"""
Throws the following error, so doesn't work yet.

RuntimeError: Visual editing of objects of type RobotModel not supported yet
"""

import klampt
import klampt.vis
import klampt.io.resource

w = klampt.WorldModel()
w.readFile(r"C:\Users\Pyro\Documents\Math4157\exoskeleton\robots\core_bot_test4.rob")

r = w.robot(0)

klampt.io.resource.edit(name=r, value=r, type="auto")