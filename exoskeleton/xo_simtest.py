import klampt
import klampt.vis
import klampt.sim.simulation
import klampt.io
import math

#Initializing the world
w = klampt.io.load('WorldModel', r'C:\Users\Pyro\Documents\Math4157\Klampt-examples\data\simulation_test_worlds\stiffness_test.xml')
num = w.numIDs()

print("Number of IDs in the world: ", num)

#Creating the simulation
sim = klampt.Simulator(w)
dt = .1
sim.setGravity((0,0,-10))
ttime = 0

#Adding it to the world. No further elements can be added
klampt.vis.add("world", w)

klampt.vis.run()

while ttime < 5:
    body = sim.body(num - 1) # Probably need to find a way to reference a specific body in the world
    body.applyForceAtPoint((1,1,1),(0,0,0))
    sim.simulate(dt)
    sim.updateWorld()
    ttime += .1