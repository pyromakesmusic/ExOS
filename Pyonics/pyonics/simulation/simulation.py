"""
LIBRARY IMPORTS
"""
import pandas as pd
from Pyonics.pyonics.physics import physics
from Pyonics.pyonics.control import control
import matplotlib.pyplot as plt

"""
CLASS DEFINITIONS
"""

class Simulation():

    def __init__(self, samplerate, totaltime):
        self.samplerate = samplerate
        self.totaltime = totaltime


    def total_timesamples(self, sample_rate, total_time):
        total_samples = int(sample_rate * total_time)
        return total_samples


    def sim_maker(self, sample_number):
        """
        Creates the indexed DataFrame.
        :param total_samples:
        :param smp_rate:
        :return:
        """
        headers = ["time", "mass", "disturbance_force", "error", "proportional", "integral", "derivative", "control",
                   "throttle_force", "total_force", "acceleration", "velocity", "position"] # This could change later so I can keep track of more joint angles
        df = pd.DataFrame(columns=headers, index=range(sample_number))
        return df

    def time_samples_to_df(self, time_sample_list):
        """
        Turns a list of time sample coordinates into a DataFrame.
        """
        values_gotten = [time_sample_list[0].get(), time_sample_list[1].get()]

        sample_number = int(self.total_timesamples(values_gotten[0], values_gotten[1]))
        values_gotten.append(sample_number)

        for i in time_sample_list[2::1]:
            values_gotten.append(i.get())

        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                         "control_constant"] # This may also change to be more adaptable to any number of joint angles or parameters

        df = pd.DataFrame(data=values_gotten, index=values_labels).T
        return df

    def simulate(self, init_params):  # This should be taking a DataFrame and returning all the program logic

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
        df = time(sample_number, sample_freq, time_series)
        df.set_index(df["time"])

        # Initialization stuff - this will probably be replaced later with calls to variables or GUI elements
        df.at[0, "error"] = 0  # This should definitely still be initialized at 0
        df.at[0, "control"] = 0  # This should also still initialize at 0
        df.at[0, "throttle_force"] = 0  # This should initialize at 0 except under weird circumstances
        df.at[0, "total_force"] = 0  # This can be whatever; the disturbance force isn't necessarily zero at start
        df.at[0, "acceleration"] = init_params["accel_start"][
            0]  # This is also not necessarily zero, it includes an initial acceleration, but can be calculated instantaneously
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
        graph = plt.plot(df["time"], df["velocity"])
        plt.draw()
        return df


class PhysicsSim(Simulation):
    def __init__(self):
        return
    pass


"""
FUNCTION DEFINITIONS
"""


def total_timesamples(sample_rate, total_time):
    total_samples = int(sample_rate * total_time)
    return total_samples


def sim_maker(sample_number):
    """
    Creates the indexed DataFrame.
    :param total_samples:
    :param smp_rate:
    :return:
    """
    headers = ["time", "mass", "disturbance_force", "error", "proportional", "integral", "derivative", "control",
               "throttle_force", "total_force", "acceleration", "velocity",
               "position"]  # This could change later so I can keep track of more joint angles
    df = pd.DataFrame(columns=headers, index=range(sample_number))
    return df


def time_samples_to_df(time_sample_list):
    """
    Turns a list of time sample coordinates into a DataFrame.
    """
    values_gotten = [time_sample_list[0].get(), time_sample_list[1].get()]

    sample_number = int(total_timesamples(values_gotten[0], values_gotten[1]))
    values_gotten.append(sample_number)

    for i in time_sample_list[2::1]:
        values_gotten.append(i.get())

    values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                     "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                     "control_constant"]  # This may also change to be more adaptable to any number of joint angles or parameters

    df = pd.DataFrame(data=values_gotten, index=values_labels).T
    return df


def simulate(init_params):  # This should be taking a DataFrame and returning all the program logic

    sample_number = int(init_params["sample_number"][0])
    sample_freq = int(init_params["sample_freq"][0])
    disturbance_const = float(init_params["scale_factor"][0])

    set_point = float(init_params["set_point"][0])
    p_k = float(init_params["p_k"][0])
    i_k = float(init_params["i_k"][0])
    d_k = float(init_params["d_k"][0])
    control_const = float(init_params["control_constant"][0])

    # Starts making the dataframe here
    time_series = sim_maker(sample_number)
    df = physics.time(sample_number, sample_freq, time_series)
    df.set_index(df["time"])

    # Initialization stuff - this will probably be replaced later with calls to variables or GUI elements
    df.at[0, "error"] = 0  # This should definitely still be initialized at 0
    df.at[0, "control"] = 0  # This should also still initialize at 0
    df.at[0, "throttle_force"] = 0  # This should initialize at 0 except under weird circumstances
    df.at[0, "total_force"] = 0  # This can be whatever; the disturbance force isn't necessarily zero at start
    df.at[0, "acceleration"] = init_params["accel_start"][
        0]  # This is also not necessarily zero, it includes an initial acceleration, but can be calculated instantaneously
    df.at[0, "velocity"] = init_params["vel_start"][0]  # Not necessarily 0, may be some v0
    df.at[0, "position"] = init_params["pos_start"][0]  # Definitely not necessarily zero

    # Filling out the columns that we can do in one go
    df = physics.mass(sample_number, df)
    df = physics.disturbance_force(sample_number, df, disturbance_const)

    # This loop is handling all of the things that need to be calculated one time-step/row at a time, instead of being filled out at the beginning.
    for x in range(0, sample_number):
        df = physics.throttle_force(df, x)
        df = physics.total_force(df, x)
        df = physics.acceleration(df, x)
        df = physics.velocity(df, x)
        df = physics.position(df, x)
        df = control.error(set_point, df, x)
        df = control.pid(df, x, p_k, i_k, d_k, control_const)
    graph = plt.plot(df["time"], df["velocity"])
    plt.draw()
    return df


def sim_and_plot(init_vals_df, ax):
    simulate(init_vals_df).plot(x="time", y="velocity", ax=ax)
    return


def main():
    return


if __name__ == "__main__":
    main()