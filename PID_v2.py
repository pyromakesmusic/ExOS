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
import matplotlib.backends.backend_tkagg as tkagg
import ipywidgets as widgets
from IPython.display import display
import numpy as np
import pandas as pd
import math
import matplotlib as mpl
import matplotlib.pyplot as plt


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
====================
"""


def total_samples(sample_rate=20, total_time=20):
    total_samples = int(sample_rate * total_time)
    return total_samples


def row_maker(total_samples):
    """
    Creates the indexed DataFrame.
    :param total_samples:
    :param smp_rate:
    :return:
    """
    headers = ["time","mass", "disturbance_force", "error", "proportional", "integral", "derivative", "pid", "throttle_force", "total_force", "acceleration", "velocity", "position"]
    df = pd.DataFrame(columns=headers, index=range(total_samples))
    return df

def cmdline_logic():
    user_input = input("Simulate? [yes/no]: ")
    while user_input == "yes":
        sample_freq = int(input("Sample rate in Hz (int): "))
        print(sample_freq)
        sample_length = int(input("Total time in seconds (int): "))
        print(sample_length)
        sample_number = int(total_samples(sample_freq, sample_length))
        print("Total number of samples:", sample_number)
        set_point = float(input("Set point for cruise control (float): "))
        print(set_point)
        pos_start = float(input("Start position (float): "))
        print(pos_start)
        vel_start = float(input("Start velocity (float): "))
        print(vel_start)
        accel_start = float(input("Start acceleration (float): "))
        print(accel_start)
        t_start = int(input("Start time value (int): "))
        print(t_start)
        t_end = int(input("End time value (int): "))
        print(t_end)
        mass = float(input("Mass (float): "))
        print(mass)
        scale_factor = float(input("Scaling factor for external disturbance (float): "))
        print(scale_factor)
        p_k = float(input("Proportional scaling factor (float): "))
        print(p_k)
        i_k = float(input("Integral scaling factor (float): "))
        print(i_k)
        d_k = float(input("Derivative scaling factor (float): "))
        print(d_k)
        control_constant = float(input("Constant multiple for PID term to throttle output (float): "))
        print(control_constant)
        control_sign = int(input("Sign of throttle vs. PID: "))
        print(control_sign)

        param_list = [sample_length, sample_freq, sample_number, pos_start, vel_start, accel_start, t_start, t_end,
                      mass,
                      scale_factor, set_point, p_k, i_k, d_k, control_constant, control_sign]
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "t_start", "t_end",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k", "control_constant", "control_sign"]
        initialparams = pd.DataFrame(data=param_list, index=values_labels).T
        # Need to pay attention to what this returns, this is critical for initialization
        print("Simulating. . .")
        print(".")
        print(". .")
        print(". . .")
        simulate(initialparams)
        user_input = ("Simulate again? [yes/no]: ")
    return initialparams

def initialize():
    """
    Just gets some initial information from the user about the time resolution.
    :return:
    """
    gui_mode = (input("Run in GUI mode? [y/n] "))
    if gui_mode == "y":
        gui_type = input("Input mode? [ipython/tkinter] ")
        gui(gui_type)

    elif gui_mode == "n":
        cmdline_logic()
    else:
        return
def simulate(init_params): # This should be taking a DataFrame and returning all the program logic

    print("sample number: ", init_params["sample_number"][0])
    print(init_params)
    sample_number = int(init_params["sample_number"][0])
    sample_freq = int(init_params["sample_freq"][0])
    disturbance_const = float(init_params["scale_factor"][0])

    set_point = float(init_params["set_point"][0])
    p_k = float(init_params["p_k"][0])
    i_k = float(init_params["i_k"][0])
    d_k = float(init_params["d_k"][0])
    control_const = float(init_params["control_constant"][0])

    # Starts making the dataframe here
    time_series = row_maker(sample_number)
    print(time_series)
    df = time(sample_number, sample_freq, time_series)
    print(df)
    df.set_index(df["time"])

    # Initialization stuff - this will probably be replaced later with calls to variables or GUI elements
    df.at[0, "error"] = 0  # This should definitely still be initialized at 0
    df.at[0, "pid"] = 0  # This should also still initialize at 0
    df.at[0, "throttle_force"] = 0  # This should initialize at 0 except under weird circumstances
    df.at[0, "total_force"] = 0  # This can be whatever; the disturbance force isn't necessarily zero at start
    df.at[0, "acceleration"] = init_params["accel_start"][0]  # This is also not necessarily zero, it includes an initial acceleration, but can be calculated instantaneously
    df.at[0, "velocity"] = init_params["vel_start"][0]  # Not necessarily 0, may be some v0
    df.at[0, "position"] = init_params["pos_start"][0]  # Definitely not necessarily zero

    # Filling out the columns that we can do in one go
    df = mass(sample_number, df)
    df = disturbance_force(sample_number, df, disturbance_const)

    # This loop is handling all of the things that need to be calculated one time-step/row at a time, instead of being filled out at the beginning.
    for x in range(0, sample_number):
        df = throttle_force(df, x)
        df = total_force(df, x)
        df = acceleration(df, x)
        df = velocity(df, x)
        df = position(df, x)
        df = error(set_point, df, x)
        df = pid(df, x, p_k, i_k, d_k, control_const)

    print(df)
    graph = plt.plot(df["time"], df["velocity"])
    plt.show()
    return df

def gui(mode):

    """
    Initialization Parameters
    """
    # Two options for GUI
    # Kinematic parameters
    if mode == "ipython":
        sample_length_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )
        sample_freq_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )
        position_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )

        velocity_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Vel_0",
            value=0
        )

        accel_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Accel_0",
            value=0
        )

        t_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="T_Start",
            value=0
        )

        t_end_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="T_End",
            value=0
        )

        mass_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )

        scale_factor_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Dist Factor",
            value=0
        )

        # PID parameters

        set_point_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Set Point",
            value=0
        )

        p_k_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="P_K",
            value=0
        )

        i_k_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="I_K",
            value=0
        )

        d_k_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="D_K",
            value=0
        )

        # Control constant
        control_constant_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Ctrl Const",
            value=0
        )

        # This should be a checkbox that just flips
        control_sign_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Ctrl Sign",
            value=0
        )
        widget_list = [sample_length_slider, sample_freq_slider, position_start_slider, velocity_start_slider, accel_start_slider, t_start_slider, t_end_slider,
                       mass_slider, scale_factor_slider, set_point_slider, p_k_slider, i_k_slider, d_k_slider,
                       control_constant_slider, control_sign_slider]
        for item in widget_list:
            display(item)

        sample_length = sample_length_slider.value
        sample_freq = sample_freq_slider.value
        pos_start = position_start_slider.value
        vel_start = velocity_start_slider.value
        accel_start = accel_start_slider.value
        t_start = t_start_slider.value
        t_end = t_end_slider.value
        mass = mass_slider.value
        scale_factor = scale_factor_slider.value
        set_point = set_point_slider.value
        p_k = p_k_slider.value
        i_k = i_k_slider.value
        d_k = d_k_slider.value
        control_constant = control_constant_slider.value
        control_sign = control_sign_slider.value
        sample_number = int(total_samples(sample_freq, sample_length))
        values = [sample_length, sample_freq, sample_number, pos_start, vel_start, accel_start, t_start, t_end, mass,
                  scale_factor, set_point, p_k, i_k, d_k, control_constant, control_sign]

    elif mode == "tkinter": # the tkinter section
        # Creates the main window
        frame = tk.Tk()
        frame.title("PID Controller v1.a")

        sample_length = tk.IntVar() # seconds
        sample_freq = tk.IntVar() # Hz
        sample_number = int(total_samples(sample_freq.get(), sample_length.get()))
        pos_start = tk.DoubleVar()  # meters
        vel_start = tk.DoubleVar()  # m/s
        accel_start = tk.DoubleVar()  # m/s^2
        t_start = tk.IntVar()  # seconds
        t_end = tk.IntVar()  # seconds
        mass = tk.DoubleVar()  # kilograms
        # PID parameters
        set_point = tk.DoubleVar()  # float(input("Set point of speed to maintain? "))
        p_k = tk.DoubleVar()  # float(input("Proportional term? "))
        i_k = tk.DoubleVar()  # float(input("Integral term? "))
        d_k = tk.DoubleVar()  # float(input("Derivative term? "))
        scale_factor = tk.DoubleVar()  # float(input("Scaling factor for external disturbance? "))
        control_constant = tk.DoubleVar()  # this is your k omega
        control_sign = tk.IntVar()  # this should be a checkbox

        """
        Initialization Parameters
        """
        sample_length_slider = tk.Scale(
            frame,
            from_ = 10,
            to = 100,
            orient = "horizontal",
            variable = sample_length)
        sample_freq_slider = tk.Scale(
            frame,
            from_ = 37,
            to = 100,
            orient = "horizontal",
            variable = sample_freq)
        # Kinematic parameters
        position_start_slider = tk.Scale(
            frame,
            from_ = 10,
            to = 100,
            orient = "horizontal",
            variable = pos_start)
        velocity_start_slider = tk.Scale(
            frame,
            from_ = 37,
            to = 100,
            orient = "horizontal",
            variable = vel_start)
        accel_start_slider = tk.Scale(
            frame,
            from_= 16,
            to = 100,
            orient = "horizontal",
            variable = accel_start)
        t_start_slider = tk.Scale(
            frame,
            from_ = 1,
            to = 100,
            orient = "horizontal",
            variable = t_start)
        t_end_slider = tk.Scale(
            frame,
            from_ = 53,
            to = 100,
            orient = "horizontal",
            variable = t_end)
        mass_slider = tk.Scale(
            frame,
            from_ = 2,
            to = 100,
            orient = "horizontal",
            variable = mass)
        scale_factor_slider = tk.Scale(
            frame,
            from_ = 2,
            to = 100,
            orient = "horizontal",
            variable = scale_factor)
        # PID parameters
        set_point_slider = tk.Scale(
            frame,
            from_ = 10,
            to = 100,
            orient = "horizontal",
            variable = set_point)
        p_k_slider = tk.Scale(
            frame,
            from_ = 37,
            to = 100,
            orient = "horizontal",
            variable=p_k)
        i_k_slider = tk.Scale(
            frame,
            from_ = 16,
            to = 100,
            orient="horizontal",
            variable = i_k)
        d_k_slider = tk.Scale(
            frame,
            from_ = 1,
            to = 100,
            orient = "horizontal",
            variable = d_k)
        # Control constant
        control_constant_slider = tk.Scale(
            frame,
            from_ = 53,
            to = 100,
            orient = "horizontal",
            variable = control_constant)
        # This should be a checkbox that just flips
        control_sign_slider = tk.Scale(
            frame,
            from_ = 2,
            to = 100,
            orient = "horizontal",
            variable = control_sign)

        initial_values = [sample_length.get(), sample_freq.get(), sample_number, pos_start.get(), vel_start.get(),
                          accel_start.get(), t_start.get(), t_end.get(), mass.get(),
                          scale_factor.get(), set_point.get(), p_k.get(), i_k.get(), d_k.get(), control_constant.get(),
                          control_sign.get()]
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "t_start", "t_end", "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                         "control_constant", "control_sign"]
        initial_values_df = pd.DataFrame(data=initial_values, index=values_labels).T

        # This button should run the simulation and probably plot it, at least depending on a checkbox
        simulate_button = tk.Button(
            frame,
            command=simulate(initial_values_df)
        )
        widget_list = [sample_length_slider, sample_freq_slider, position_start_slider, velocity_start_slider, accel_start_slider, t_start_slider, t_end_slider,
                       mass_slider, scale_factor_slider, set_point_slider, p_k_slider, i_k_slider, d_k_slider,
                       control_constant_slider, control_sign_slider, simulate_button]

        for item in widget_list:
            item.pack()
        frame.mainloop()


    throttle_f = 0.0  # initial force applied by throttle = 0

    return

def noise_f(k):
    whitenoise = np.random.normal(1,2)
    scaled_noise = k * whitenoise
    return scaled_noise

def time(num_samples, sample_rate, df):
    """
    Enters the time value into the dataframe.
    :param num_samples:
    :param sample_rate:
    :param df:
    :return:
    """
    print(num_samples)
    time_value_list = list((x * (1/sample_rate) for x in range(num_samples)))
    time_value_series = pd.Series(data=time_value_list)
    df["time"] = time_value_series
    return df

def mass(num_samples, df):
    """
    Enters the mass into the DataFrame.
    :param num_samples:
    :param df:
    :return:
    """
    mass = 1
    mass_list = []
    for i in range(num_samples):
        mass_list.append(mass)
    mass_series = pd.Series(data = mass_list)
    df["mass"] = mass_series
    return df
def disturbance_force(num_samples, df, disturbance_constant):
    """
    Returns a disturbance force.
    :param num_samples:
    :param df:
    :return:
    """
    disturbance = 1 * disturbance_constant
    disturbance_list = []
    for i in range(num_samples):
        disturbance_list.append(disturbance)
    disturbance_series = pd.Series(data = disturbance_list)
    df["disturbance_force"] = disturbance_series
    return df

def throttle_force(df, i):
    """
    Returns a throttle force.
    :param df:
    :param i:
    :return:
    """

    if i == 0:
        force = 0
    else:
        pid = df.at[(i - 1), "pid"]
        force = pid
    df.at[i, "throttle_force"] = force
    return df

def total_force(df, i):
    """
    Returns the total force.
    :param df:
    :param i:
    :return:
    """
    total_f = df.at[i, "throttle_force"] + df.at[i, "disturbance_force"]
    df.at[i, "total_force"] = total_f
    return df
    
def acceleration(df, i):
    """
    Calculates the instantaneous acceleration.
    :param df: DataFrame containing force and mass columns, plus a time column.
    :param i: Time point at which to calculate.
    :return: DataFrame with the acceleration at that time point filled in.
    """
    accel = df.at[i, "total_force"] / df.at[i, "mass"]
    df.at[i, "acceleration"] = accel
    return df

def velocity(df, i):
    df_abridged = df[0:i]
    velocity = np.trapz(y=df_abridged["acceleration"], x=df_abridged["time"])
    """
    Calculates the velocity.
    :param df:
    :param i:
    :return:
    """
    df.at[i, "velocity"] = velocity
    return df

def position(df, i):
    """
    Calculates the position.
    :param df:
    :param i:
    :return:
    """
    df_abridged = df[0:i]
    position = np.trapz(y=df_abridged["velocity"], x=df_abridged["time"])
    df.at[i, "position"] = position
    return df

def error(set_point, df, i):
    """
    Determines the error.
    :param process_variable:
    :param set_point:
    :param df: main dataframe
    :param i: time step
    :return: modified dataframe
    """
    error = set_point - df.at[i, "velocity"]
    df.at[i, "error"] = error
    return df

def pid(df, i, p_k, i_k, d_k, scaling_factor):
    """
    Performs the PID logic.
    :param df: main dataframe
    :param i: time step
    :return: modified dataframe
    """
    df_abridged = df[0:i]
    proportional = p_k * df.at[i, "error"]
    integral = i_k * np.trapz(df_abridged["error"])
    derivative = d_k * df.at[i, "error"]
    pid = scaling_factor * (proportional + integral + derivative)
    df.at[i, "proportional"] = proportional
    df.at[i, "integral"] = integral
    df.at[i, "derivative"] = derivative
    df.at[i, "pid"] = pid
#    print("P:",proportional," I:", integral," D:", derivative," PID:", pid)
    return df

def main():
    initialize()
    return

main()