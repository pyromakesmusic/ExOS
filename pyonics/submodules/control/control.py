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
class PIDKernel():

    def output(self):
        print(self.data)
        return(self.data)

    def __init__(self, time, process_variable, set_point, k_p, k_i, k_d): # Each a pd.Series of scalars
        self.time = time
        self.process_variable = process_variable
        self.set_point = set_point
        self.error = set_point - process_variable # Not sure if naive subtraction will work on DataFrames but we will see
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.data = pd.concat(self.time, self.process_variable, self.error, self.set_point, self.k_p, self.k_i, self.k_d)

@dataclass
class PIDController():
    pass


"""
MAIN FUNCTION
"""

def main():
    kernel1 = PIDKernel()
    control1 = PIDController(kernel1)
    pass

if __name__ == "__main__":
    main()