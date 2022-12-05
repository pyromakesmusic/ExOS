"""
DEVELOPER COMMENTS

This should probably also be a core element and not have external dependencies.
"""

"""
LIBRARY IMPORTS
"""
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass

"""
FUNCTION DEFINITIONS
"""


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
    if i < 2:
        derivative = 0
    else:
        gradient = np.gradient(df_abridged["error"])
        derivative = d_k * float(gradient[-2:-1])
    pid = scaling_factor * (proportional + integral + derivative)
    df.at[i, "proportional"] = proportional
    df.at[i, "integral"] = integral
    df.at[i, "derivative"] = derivative
    df.at[i, "control"] = pid
    return df

"""
CLASS DEFINITIONS
"""
@dataclass
class PIDKernel(): # Should be a DataFrame built from a set of Series of scalar values
    # Each of these should be a series of scalars, may need to make more dataclasses for each series
    time: object
    process_variable: object
    set_point: object
    k_p: object
    k_i: object
    k_d: object

class PIDController():

    def __init__(self, process_variable, set_point, k_p, k_i, k_d): # Need a dataframe holding scalar values should both be scalars, can be negative for orientation
        self.process_variable = process_variable
        self.set_point = set_point
        self.error = set_point - process_variable
        self.p = k_p * self.error
        self.i = k_i * self.error
        self.d = k_d * self.error
