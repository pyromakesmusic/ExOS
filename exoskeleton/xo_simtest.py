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

klampt.vis.show()

while klampt.vis.shown(): # I'm not sure this loop is running at all
    body = sim.body(w.rigidObject(2)) # Probably need to find a way to reference a specific body in the world
    print(body)
    body.applyForceAtPoint((1,1,1),(0,0,0))
    sim.simulate(dt)
    sim.updateWorld()
    ttime += .1