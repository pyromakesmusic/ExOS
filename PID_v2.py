# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 21:55:28 2022

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
window = tk.Tk()
window.title("PID Controller v1.a")
frame = ttk.Frame(window, padding = 10)


"""
GLOBALS
"""

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

initial_params = [POS_START.get(), VEL_START.get(), ACCEL_START.get(), MASS.get(), T_START.get(), T_END.get()]

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

"""
FUNCTION DEFINITIONS
"""

def noise_f(k):
    whitenoise = np.random.normal(1,2)
    scaled_noise = k * whitenoise
    return scaled_noise

def kinematics(df, t): # 
    keys_list = ["time", "disturbance_f", "throttle_f", "total_f", "mass", "acceleration", "velocity", "position"]
    
    return(df)

def error_func(df, set_point, time): # Think this needs to reference the whole dataframe history?
    error = 1

    p_e = P_K.get() * error
    i_e = I_K.get() * error
    d_e = D_K.get() * error
    pid = p_e + i_e + d_e
    
    return pid

def pid(df, parameter_list): # This should be able to reference the whole DataFrame's history
    pid_list = [1, throttle_f]
    keys_list = ["PID", "throttle force"]
    output_df = pd.DataFrame(data = pid_list, index = keys_list)
    return output_df

def plot(x, y, **args):
    # figure contains plot
    fig = mpl.figure.Figure(figsize = (5, 2), dpi = 300)
    x.hist()
    
    canvas = mpl.backends.backend_tkagg.FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = mpl.backends.backend_tkagg.NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas.get_tk_widget().pack()

