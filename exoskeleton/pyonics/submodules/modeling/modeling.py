"""
LIBRARY IMPORTS
"""
import pandas as pd
from exoskeleton import pyonics as phys
import exoskeleton.pyonics.submodules.control.control as ctrl
import matplotlib.pyplot as plt


"""
FUNCTION DEFINITIONS
"""


# Main Function
def main():
    sim_parameter_data = sim_parameter_getter()
    time_axis = TimeAxis(sim_parameter_data) # I don't think I've actually done anything with this yet
    ctrl1_params = ctrl.pid_parameter_getter()
    controller1 = ctrl.PIDController(ctrl1_params)
    m, pos, vel, acc, f_n, strainmod = physbody_parameter_getter()
    automaton = Automaton(controller1, m, pos, vel, acc, f_n, strainmod) # Contains a physics body plus a controller


    physics_bodies = [automaton]
    engine = Simulation(time_axis, physics_bodies)
    print(engine)
    print(automaton)
    return


# Main Function Call
if __name__ == "__main__":
    main()