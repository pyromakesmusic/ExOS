"""
LIBRARY IMPORTS
"""
import pandas as pd
import pyonics.submodules.physics as phys
import pyonics.submodules.control as ctrl
import pyonics.submodules.interface as pinter # This will eventually be a circular import, remember to remove it
import matplotlib.pyplot as plt


"""
FUNCTION DEFINITIONS
"""

def total_num_samples_getter(sample_rate, total_time):
    total_samples = int(sample_rate * total_time)
    return total_samples


def sim_maker_defunct(sample_number):
    """
    Creates the indexed DataFrame.
    """
    headers = ["time"]
    df = pd.DataFrame(columns=headers, index=range(sample_number))
    return df


def time_samples_to_df(time_sample_list):
    """
    Turns a list of time sample coordinates into a DataFrame.
    """
    values_gotten = [time_sample_list[0].get(), time_sample_list[1].get()]
    sample_number = int(total_num_samples_getter(values_gotten[0], values_gotten[1]))
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
    time_series = sim_maker_defunct(sample_number)
    df = phys.time(sample_number, sample_freq, time_series)
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
    df = phys.mass(sample_number, df)
    df = phys.disturbance_force(sample_number, df, disturbance_const)

    # This loop is handling all of the things that need to be calculated one time-step/row at a time, instead of being filled out at the beginning.
    for x in range(0, sample_number):
        df = phys.throttle_force(df, x)
        df = phys.total_force(df, x)
        df = phys.acceleration(df, x)
        df = phys.velocity(df, x)
        df = phys.position(df, x)
        df = ctrl.error(set_point, df, x)
        df = ctrl.pid(df, x, p_k, i_k, d_k, control_const)
    graph = plt.plot(df["time"], df["velocity"])
    plt.draw()
    return df


def sim_and_plot(init_vals_df, ax):
    simulate(init_vals_df).plot(x="time", y="velocity", ax=ax)
    return

def terminal_prompt():
    sample_freq = int(input("Sample rate in Hz (int): "))
    print(sample_freq)
    sample_length = int(input("Total time in seconds (int): "))
    print(sample_length)
    sample_number = int(total_num_samples_getter(sample_freq, sample_length))
    print("Total number of samples:", sample_number)
    labels = ["sample_length", "sample_freq", "sample_number"]
    simulation_parameters = pd.DataFrame(data=[sample_length,sample_freq,sample_number], index=labels)
    print(simulation_parameters.keys)
    return simulation_parameters



"""
CLASS DEFINITIONS
"""

class TimeAxis: # Should be a type of dataframe

    def __init__(self, initial_df): #timeparams contains sample frequency, total time
        print(initial_df.index)
        length_row = initial_df.iloc[2]
        length = range(length_row[0])
        self.time_axis = pd.DataFrame(index=length) # Here is a good place to add the columns, or maybe that happens in the larger simulation thing
        print(self.time_axis)

class Simulation:

    def __init__(self, time_axis, physics_bodies): #physics_bodies is a list of calculated particles each with parameters
        pass

# Main Function
def main():
    bodies = []
    sim_parameter_data = terminal_prompt()
    print(sim_parameter_data)
    time_axis = TimeAxis(sim_parameter_data)
    print(time_axis)
    engine = Simulation(sim_parameter_data, bodies)
    return


# Main Function Call
if __name__ == "__main__":
    main()