# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 19:26:42 2022
Priority Code Cell
@author: Ghost
===============
Questions, Thoughts, Notes, etc.
--------------------------------
DATE: Sept 30

To address the question more generally, I probably need to model the kinematics
first, then get the error term from that. The kinematic equations may have libraries for solving them.

1735h
I'm going to do it. Build the kinematics library first, build in sliders (probably) so I don't have to input everything every single time.

DATE: Oct 1

1323h
Probably start with the GUI, then kinematics, then error.

===============
LIBRARY IMPORTS
"""
import tkinter as tk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import turtle


"""
GUI
"""
window = tk.Tk()
# datalog = pd.DataFrame(columns = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"])

POS_START = 0.0 # meters
VEL_START = 0.0 # m/s
ACCEL_START = 0.0 # m/s^2
T_START = 0 # seconds
T_END = 100 # seconds
MASS = 1.0 # kilograms

throttle_f = 0 # initial force applied by throttle = 0

set_point = 50 #float(input("Set point of speed to maintain? "))
p = 1 #float(input("Proportional term? "))
i = 1 #float(input("Integral term? "))
d = 1 #float(input("Derivative term? "))
scaling_factor = 4#float(input("Scaling factor for external disturbance? "))
control_constant = .5 #float(input("Constant to multiply the PID term by? "))
control_sign = 1 #int(input("-1 or 1 to multiply by? "))

def noise_f(k):
  whitenoise = np.random.normal(0,1,100)
  scaled_noise = k * whitenoise
  return scaled_noise

def accel():
  return 0

def velo():
  return 0

def pos():
  return 0

def error_func():
  return 0

def pid():
  return 0



def time_step(startpos, startvel, startacc, m, start_time, end_time): # m is mass
  """
  Should be the main loop. Takes in parameters and returns a dataframe of what happens to our mass over our time range.
  Since we always have to sum up from 0 up to t for the integral, does it make sense to feed a dataframe to the control loop?
  Sept 30 1755h - This probably needs to be heavily refactored and broken up into function calls of the functions listed above.
  """
  
  column_names = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"]
  throttle_f = 0
  df_list = []
  for step in range(start_time, end_time):
    external_f = noise_f(scaling_factor)
    total_f = external_f + throttle_f
    accel = total_f/m
    velo = 1 # Here goes an integral
    pos = 1 # here goes an integral of velocity
    error = abs(set_point - velo)
    prop_term = p * error
    int_term = i * error # need to do an integral here
    der_term = d * error # need to do a derivative here
    pid_term = (prop_term + int_term + der_term) * control_constant * control_sign
    throttle_f = pid_term
    row = [step, pos, velo, error, accel, external_f, throttle_f, total_f]
    row_df = pd.DataFrame(data=row)

    df_list.append(row_df)
#    time_row = {"time" : step, "position" : pos, "velocity" : velo, "velocity-error" : error, "acceleration" : accel, "disturbance force" : external_f, "throttle" : throttle_f, "total force" : total_f}
#    ser = pd.DataFrame(data=time_row, index = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"])
#    print(ser)
#    row_list.append(ser)
  final = pd.concat(df_list, join="inner", axis = 1).T
  final.columns = (column_names)
  final.index = final["time"]

  return(final)
values = time_step(POS_START, VEL_START, ACCEL_START, MASS, T_START, T_END)
# columns = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"]


timevals = values["time"]
ext_f_vals = values["disturbance force"]

plt.plot(timevals)