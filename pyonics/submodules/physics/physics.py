"""
DEVELOPER COMMENTS
==================

This should have no internal dependencies and should serve as a usable kernel to start building up the library from
its first principles.
"""


"""
LIBRARY IMPORTS
"""

# Standard Libraries
import os
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass


# Third Party Libraries

"""
FUNCTION DEFINITIONS
"""



def time(num_samples, sample_rate, df):
    """
    Enters the time value into the dataframe.
    :param num_samples:
    :param sample_rate:
    :param df:
    :return:
    """
    time_value_list = list((x * (1 / sample_rate) for x in range(num_samples)))
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
    mass_series = pd.Series(data=mass_list)
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
    disturbance_series = pd.Series(data=disturbance_list)
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
            force = df.at[(i - 1), "control"]
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

"""
Forces
"""


def noise_f(k):
    whitenoise = np.random.normal(1, 2)
    scaled_noise = k * whitenoise
    return scaled_noise


"""
CLASS DEFINITIONS
"""
@dataclass
class PhysicsBody(): # For kinematic definition - a dataframe characterizing the physical state of an entity. Assume XYZ
    mass: float
    pos_xyz: tuple
    vel_xyz: tuple
    acc_xyz: tuple
    throttle_force: tuple
    net_force: tuple
    youngs_modulus: float
    bulk_modulus: float
    shear_modulus: float

@dataclass
class RigidBody(PhysicsBody):
    """
    Should be used for any rigid object undergound physics calculations
    """

@dataclass
class HardLink(RigidBody):
    """
    Parent class used for any structurally important element of the exoskeleton.
    """

@dataclass
class BoneLink(HardLink):
    """
    Should be used to represent rigid load-bearing non-joint members of the exoskeleton
    """
    pass

@dataclass
class JointLink(HardLink):
    """
    Should be used to represent joints
    """
    pass

@dataclass
class SoftBody(PhysicsBody):
    pass
@dataclass
class Exoskeleton(PhysicsBody):
    pass
@dataclass
class PhysicsFrame():
    """
    A particular physical (not necessarily inertial?) reference frame
    """
    time: float
    time_interval: float # seconds


"""
Main
"""

def main():
    for path in sys.path:
        print(path)
    return

if __name__ == "__main__":
    main()