# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 21:55:28 2022
===============
Document Comments:
    10.11.22
    2218h 
    I think the index should be separate from the time values. Physics should 
    be based on time independent of the index so that I can have a consistent 
    indexing scheme regardless of the time resolution of the data.

===============
LIBRARY IMPORTS
"""
import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from scipy.integrate import odeint
import turtle


"""
CONFIG
"""
pd.options.display.width = 0
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

"""
GUI Initialization
"""


"""
GLOBALS
"""


"""
FUNCTION DEFINITIONS
"""

def gui():
    window = tk.Tk()
    window.title("PID Controller v1.a")
    frame = ttk.Frame(window, padding = 10)
    
    POS_START = tk.DoubleVar() # meters
    VEL_START =  tk.DoubleVar() # m/s
    ACCEL_START =  tk.DoubleVar() # m/s^2
    T_START =  tk.IntVar() # seconds
    T_END =  tk.IntVar() # seconds

    MASS =  tk.DoubleVar() # kilograms

    # PID parameters
    SET_POINT = tk.DoubleVar() # float(input("Set point of speed to maintain? "))
    P_K = tk.DoubleVar() # float(input("Proportional term? "))
    I_K = tk.DoubleVar() # float(input("Integral term? "))
    D_K = tk.DoubleVar() # float(input("Derivative term? "))
    SCALE_FACTOR = tk.DoubleVar() #float(input("Scaling factor for external disturbance? "))
    CONTROL_CONSTANT = tk.DoubleVar() # this is your k omega
    CONTROL_SIGN = True # this should be a checkbox
    throttle_f = 0.0 # initial force applied by throttle = 0

    """
    Initialization Parameters
    """
    # Kinematic parameters

    position_start_slider = ttk.Scale(
        frame,
        from_ = 10,
        to = 100,
        orient = "horizontal",
        variable = POS_START)

    velocity_start_slider = ttk.Scale(
        frame,
        from_ = 37,
        to = 100,
        orient = "horizontal",
        variable = VEL_START) 

    accel_start_slider = tk.Scale(
        frame,
        from_ = 16,
        to = 100,
        orient = "horizontal",
        variable = ACCEL_START) 

    t_start_slider = tk.Scale(
        frame,
        from_ = 1,
        to = 100,
        orient = "horizontal",
        variable = T_START) 

    t_end_slider = tk.Scale(
        frame,
        from_ = 53,
        to = 100,
        orient = "horizontal",
        variable = T_END) 

    mass_slider = tk.Scale(
        frame,
        from_ = 2,
        to = 100,
        orient = "horizontal",
        variable = MASS)

    scale_factor_slider = tk.Scale(
        frame,
        from_ = 2,
        to = 100,
        orient = "horizontal",
        variable = SCALE_FACTOR)  


    # PID parameters

    set_point_slider = tk.Scale(
        frame,
        from_ = 10,
        to = 100,
        orient = "horizontal",
        variable = SET_POINT)

    p_k_slider = tk.Scale(
        frame,
        from_ = 37,
        to = 100,
        orient = "horizontal",
        variable = P_K) 

    i_k_slider = tk.Scale(
        frame,
        from_ = 16,
        to = 100,
        orient = "horizontal",
        variable = I_K) 

    d_k_slider = tk.Scale(
        frame,
        from_ = 1,
        to = 100,
        orient = "horizontal",
        variable = D_K) 

    # Control constant
    control_constant_slider = tk.Scale(
        frame,
        from_ = 53,
        to = 100,
        orient = "horizontal",
        variable = CONTROL_CONSTANT) 

    # This should be a checkbox that just flips
    control_sign = tk.Scale(
        frame,
        from_ = 2,
        to = 100,
        orient = "horizontal",
        variable = MASS) 
    
#    window.mainloop()
    pass

def noise_f(k):
    whitenoise = np.random.normal(1,2)
    scaled_noise = k * whitenoise
    return scaled_noise

def total_samples(sample_rate=1000, total_time=10):
    total_samples = sample_rate * total_time
    return total_samples

def mass():
    pass

def force():
    pass
    
def acceleration(force=0, mass=1):
    accel = force/mass
    return accel

def velocity(accel):
    pass

def position(velo):
    pass

def error(process_variable, set_point):
    return set_point - process_variable

def pid(error=0):
    pass

def row_maker():
    pass

def main():
    command_line = bool(input("Run in command line mode? "))
    sample_rate = int(input("Sample rate in Hz (int): "))
    total_time = int(input("Total time in seconds (int): "))
    sample_number = total_samples(sample_rate, total_time)
    for t in range(sample_number): # t is the time value
        pass
        
    pass

main()