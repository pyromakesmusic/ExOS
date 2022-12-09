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


def pid_parameter_getter():
    set_point = float(input(#"Set point: "
                            ))
    p_k = float(input(#"Proportional scaling factor (float): "
        ))
    i_k = float(input(#"Integral scaling factor (float): "
         ))
    d_k = float(input(#"Derivative scaling factor (float): "
                      ))
    control_constant = float(input(#"Constant multiple for PID term to throttle output (float): "
                                   ))
    pidparams = {
        "set_point": set_point,
        "p_k": p_k,
        "i_k": i_k,
        "d_k": d_k,
        "control_constant": control_constant
    }
    return pidparams

"""
CLASS DEFINITIONS
"""

@dataclass
class PIDController:
    def __init__(self, pid_parameters):

        self.df = pd.DataFrame()
        for tensor in pid_parameters:
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