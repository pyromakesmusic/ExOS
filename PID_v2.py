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

def gui():

    """
    Initialization Parameters
    """
    # Kinematic parameters

    position_start_slider = widgets.IntSlider(
        min=0,
        max=10,
        step=1,
        description="Pos_0",
        value=0
    )

    velocity_start_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    accel_start_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    t_start_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    t_end_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    mass_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    scale_factor_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )


    # PID parameters

    set_point_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    p_k_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    i_k_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    d_k_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    # Control constant
    control_constant_slider = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )

    # This should be a checkbox that just flips
    control_sign = widgets.IntSlider(
        min=0,
        max = 10,
        step = 1,
        description = "Pos_0",
        value = 0
    )
    
    display(control_sign)
    return 0

def noise_f(k):
    whitenoise = np.random.normal(1,2)
    scaled_noise = k * whitenoise
    return scaled_noise

def total_samples(sample_rate=20, total_time=20):
    total_samples = sample_rate * total_time
    return total_samples
def initialize():
    """
    Just gets some initial information from the user about the time resolution.
    :return:
    """
    #command_line = bool(input("Run in command line mode? "))
    sample_rate = int(input("Sample rate in Hz (int): \n"))
    print(sample_rate)
    total_time = int(input("Total time in seconds (int): \n"))
    print(total_time)
    set_point = int(input("Set point for cruise control (int): \n"))
    print(set_point)
    sample_number = total_samples(sample_rate, total_time)
    p_k = 1
    i_k = 1
    d_k = 1
    scaling_factor = .01
    return sample_number, sample_rate, set_point, p_k, i_k, d_k, scaling_factor

def row_maker(total_samples, smp_rate):
    """
    Creates the indexed DataFrame.
    :param total_samples:
    :param smp_rate:
    :return:
    """
    headers = ["time","mass", "disturbance_force", "error", "proportional", "integral", "derivative", "pid", "throttle_force", "total_force", "acceleration", "velocity", "position"]
    df = pd.DataFrame(columns=headers, index=range(total_samples))
    return df
def time(num_samples, sample_rate, df):
    """
    Enters the time value into the dataframe.
    :param num_samples:
    :param sample_rate:
    :param df:
    :return:
    """
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
def disturbance_force(num_samples, df):
    """
    Returns a disturbance force.
    :param num_samples:
    :param df:
    :return:
    """
    disturbance = 1
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
    gui()
    total_samples, sample_freq, set_point, p_k, i_k, d_k, scaling_factor = initialize()

    time_series = row_maker(total_samples, sample_freq)
    df = time(total_samples, sample_freq, time_series)
    df.set_index(df["time"])

    # Initialization stuff - this will probably be replaced later with calls to variables or GUI elements
    df.at[0, "error"] = 0
    df.at[0, "pid"] = 0
    df.at[0, "throttle_force"] = 0
    df.at[0, "total_force"] = 0
    df.at[0, "acceleration"] = 0
    df.at[0, "velocity"] = 0
    df.at[0, "position"] = 0


    # Filling out the columns that we can do in one go
    df = mass(total_samples, df)
    df = disturbance_force(total_samples, df)

    # This loop is handling all of the things that need to be calculated one time-step/row at a time, instead of being filled out at the beginning.
    for x in range(0, total_samples):
        df = throttle_force(df, x)
        df = total_force(df, x)
        df = acceleration(df, x)
        df = velocity(df, x)
        df = position(df, x)
        df = error(set_point, df, x)
        df = pid(df, x, p_k, i_k, d_k, scaling_factor)

    plt.plot(df["time"], df["velocity"])

    return 

main()