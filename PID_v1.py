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


"""
GLOBALS
"""
POS_START = tk.IntVar() # meters
VEL_START =  tk.IntVar() # m/s
ACCEL_START =  tk.IntVar() # m/s^2
T_START =  tk.IntVar() # seconds
T_END =  tk.IntVar() # seconds
MASS =  tk.IntVar() # kilograms

CALC_TEST =   test = pd.DataFrame(data=[1,2,3,4,1,2,3,4])


"""
User Input
"""
position_start_slider = tk.Scale(
    window,
    from_ = 10,
    to = 100,
    orient = "vertical",
    variable = POS_START)

velocity_start_slider = tk.Scale(
    window,
    from_ = 37,
    to = 100,
    orient = "vertical",
    variable = VEL_START) 

accel_start_slider = tk.Scale(
    window,
    from_ = 16,
    to = 100,
    orient = "vertical",
    variable = ACCEL_START) 

t_start_slider = tk.Scale(
    window,
    from_ = 1,
    to = 100,
    orient = "vertical",
    variable = T_START) 

t_end_slider = tk.Scale(
    window,
    from_ = 53,
    to = 100,
    orient = "vertical",
    variable = T_END) 

mass_slider = tk.Scale(
    window,
    from_ = 2,
    to = 100,
    orient = "vertical",
    variable = MASS) 

initial_params = [POS_START.get(), VEL_START.get(), ACCEL_START.get(), MASS.get(), T_START.get(), T_END.get()]

throttle_f = 0 # initial force applied by throttle = 0

set_point = 50 #float(input("Set point of speed to maintain? "))
p = 1 #float(input("Proportional term? "))
i = 1 #float(input("Integral term? "))
d = 1 #float(input("Derivative term? "))
scaling_factor = 4#float(input("Scaling factor for external disturbance? "))
control_constant = .5 #float(input("Constant to multiply the PID term by? "))
control_sign = 1 #int(input("-1 or 1 to multiply by? "))

def integral(diff, w_r_t, dt):
    integral_output = np.trapz(y = diff, x=w_r_t, dx=dt)
    return(integral_output)

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


def time_step_placeholderfornow(startpos, startvel, startacc, m, start_time, end_time): # m is mass
  """
  Should be the main simulation loop. Takes in parameters and returns a dataframe of what happens to our mass over our time range.
  Since we always have to sum up from 0 up to t for the integral, does it make sense to feed a dataframe to the control loop?
  Sept 30 1755h - This probably needs to be heavily refactored and broken up into function calls of the functions listed above.
  """
  print(startpos)
  print(startvel)
  print(startacc)
  print(m)
  print(start_time)
  print(end_time)
  column_names = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"]
  throttle_f = 0
  df_list = []
  test = pd.DataFrame(data=[1,2,3,4,1,2,3,4])
  #This is for testing, delete it later
  for i in range(0,99):
      df_list.append(test)
  df_list.append(test)
  print(startpos)
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
    print(row_df)
    df_list.append(row_df)

  final = pd.concat(df_list, join="inner", axis = 1).T
  final.columns = (column_names)

  plt.plot(final)
  print(final)
  return(final)

def time_step(a,b,c,d,e,f):
    # This is a placeholder function made to build out the structure of what needs to get graphed and put it on the GUI
    list = [0,2,3,4,5,6,7,8]
    dummy_df = pd.DataFrame(data = list, index = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"]).T

    return(dummy_df)

def simulation_logic(initialconditions):
    print(initialconditions)

values = time_step(POS_START.get(), VEL_START.get(), ACCEL_START.get(), MASS.get(), T_START.get(), T_END.get())
# columns = ["time","position","velocity", "velocity-error","acceleration", "disturbance force", "throttle", "total force"]


print(values)
print(values.index)
print(POS_START.get(), VEL_START.get(), ACCEL_START.get(), MASS.get(), T_START.get(), T_END.get())
timevals = values["time"]
ext_f_vals = values["disturbance force"]

times = plt.plot(timevals)

sim_button = tk.Button(master = window,
                     command = simulation_logic(initial_params),
                     height = 2,
                     width = 10,
                     text = "Plot")


velocity_values = np.trapz(ext_f_vals) + POS_START.get()
#position_values = np.trapz(velocity_values)
#print(velocity_values)
#print(position_values)


sim_button.pack()
# Main GUI call
window.mainloop()
