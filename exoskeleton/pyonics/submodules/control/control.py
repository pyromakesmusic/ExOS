"""
DEVELOPER COMMENTS

Keep at bottom level, so no references to other user-created libraries. Low level control algorithms. Probably best
to optimize with C/C++.
"""

"""
STANDARD LIBRARY IMPORTS
"""
import numpy as np

"""
OUTSIDE LIBRARY IMPORTS
"""
import klampt

"""
CLASS DEFINITIONS
"""

"""
FUNCTION DEFINITIONS
"""



def error(set_point, df, i):
    """
    Determines the error between a set point and a current value ( stored in a dataframe with i+2 steps)
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
    :param p_k: proportional value
    :param i_k: integral control value
    :param d_k: derivative control value
    :scaling_factor: factor to scale all three of P, I and D to before final output
    :return: modified dataframe
    """
    df_abridged = df[0:i]
    proportional = p_k * df.at[i, "error"] # Some constant times the error
    integral = i_k * np.trapz(df_abridged["error"]) # Trapezoid rule for discrete integral
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
MAIN FUNCTION CALL
"""

def main():
    pass

if __name__ == "__main__":
    main()