import klampt
from klampt import vis
from klampt.vis import GLRealtimeProgram

class GLTest(GLRealtimeProgram):
    """Define hooks into the GUI loop to draw and update the simulation"""
    def __init__(self,world,sim):
        GLRealtimeProgram.__init__(self,"GLTest")
        self.world = world
        self.sim = sim

    def display(self):
        self.sim.updateWorld()
        self.world.drawGL()

    def idle(self):
        rfs = sim.controller(0).sensor("RF_ForceSensor")
        print("Sensor values:",rfs.getMeasurements())
        sim.simulate(self.dt)
        return

if __name__ == "__main__":
    print("================================================================")
    print("gl_vis.py: This example demonstrates how to use the GL visualization interface")
    print("   to tie directly into the GUI.")
    print()
    print("   The demo simulates a world and reads a force sensor")
    print("================================================================")
    world = klampt.WorldModel()
    res = world.readFile("D:\#PERSONAL\#STEDWARDS\Klampt-examples\data\hubo_plane.xml")
    if not res:
        raise RuntimeError("Unable to load world")
    sim = klampt.Simulator(world)
    print("STARTING vis.run()")
    vis.run(GLTest(world,sim))
    print("END OF vis.run()")
