import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

from user_input.input_mode import gui, cmdline_logic
from pids import pid
from utils import utils


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
        error = df.at[(i - 1), "error"]
        if error != 0:
            force = df.at[(i - 1), "pid"]
        else:
            force = 0
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

def initialize():
    """
    Just gets some initial information from the user about the time resolution.
    :return:
    """
    gui_mode = (input("Run in GUI mode? [y/n]: "))
    print(gui_mode)
    if gui_mode == "y":
        gui_type = input("Input mode? [ipython/tkinter]: ")
        print(gui_type)
        gui(gui_type)

    elif gui_mode == "n":
        cmdline_logic()
    else:
        return
        
def simulate(init_params): # This should be taking a DataFrame and returning all the program logic

    sample_number = int(init_params["sample_number"][0])
    sample_freq = int(init_params["sample_freq"][0])
    disturbance_const = float(init_params["scale_factor"][0])

    set_point = float(init_params["set_point"][0])
    p_k = float(init_params["p_k"][0])
    i_k = float(init_params["i_k"][0])
    d_k = float(init_params["d_k"][0])
    control_const = float(init_params["control_constant"][0])

    # Starts making the dataframe here
    time_series = utils.row_maker(sample_number)
    df = time(sample_number, sample_freq, time_series)
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
        df = pid.pid(df, x, p_k, i_k, d_k, control_const)
    graph = plt.plot(df["time"], df["velocity"])
    # plt.draw()
    return df


def sim_and_plot(init_vals_df, ax):
    simulate(init_vals_df).plot(x="time", y="velocity", ax=ax)
    return