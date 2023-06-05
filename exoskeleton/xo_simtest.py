import klampt
import klampt.vis
import klampt.io

w = klampt.io.load('WorldModel', r'D:\#PERSONAL\#STEDWARDS\Klampt-examples\data\simulation_test_worlds\stiffness_test.xml')
klampt.vis.add("world", w)
klampt.vis.run()