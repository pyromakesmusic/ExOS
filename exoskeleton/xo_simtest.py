import klampt
import klampt.vis
import klampt.sim.simulation
import klampt.io
import math

#Initializing the world
w = klampt.io.load('WorldModel', 'xosim_world_v1.xml')
num = w.numIDs()

print("Number of IDs in the world: ", num)

#Creating the simulation
sim = klampt.Simulator(w)
dt = .5
sim.setGravity((0,0,-10))

#Adding it to the world. No further elements can be added
klampt.vis.add("world", w)

klampt.vis.show()

while klampt.vis.shown(): # I'm not sure this loop is running at all
    body = sim.body(w.rigidObject(0)) # Probably need to find a way to reference a specific body in the world
    print(body)
    sim.simulate(dt)
    sim.updateWorld()