import klampt
import klampt.vis
import klampt.sim.simulation
import klampt.io

#Initializing the world
w = klampt.io.load('WorldModel', r'C:\Users\Pyro\Documents\Math4157\Klampt-examples\data\simulation_test_worlds\stiffness_test.xml')
print("Number of IDs in the world: ", w.numIDs())

#Creating the simulation
sim = klampt.Simulator(w)
dt = .1
sim.setGravity((0,0,-10))
ttime = 0

#Adding it to the world. No further elements can be added
klampt.vis.add("world", w)

klampt.vis.run()

while ttime < 5:
    body = sim.body()
    sim.simulate(dt)
    sim.updateWorld()
    ttime += .1