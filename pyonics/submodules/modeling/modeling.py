"""
LIBRARY IMPORTS
"""
import pandas as pd
import pyonics.submodules.physics.physics as phys
import pyonics.submodules.control.control as ctrl
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

    # This loop is handling all of the things that need to be calculated one time-step/row at a time, instead of being filled out at the beginning - can probably be called as a pure physics function
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

def sim_parameter_getter(): # need versions or extensions of this for each PID controller and each physics body
    sample_freq = int(input(#"Sample rate in Hz (int): "
                            ))
    sample_length = int(input(#"Total time in seconds (int): "
                              ))
    #print(sample_length)
    sample_number = int(total_num_samples_getter(sample_freq, sample_length))
    #print("Total number of samples:", sample_number)
    labels = ["sample_length", "sample_freq", "sample_number"]
    simulation_parameters = pd.DataFrame(data=[sample_length,sample_freq,sample_number], index=labels)
    #print(simulation_parameters.keys)
    return simulation_parameters

def physbody_parameter_getter():
    mass = float(input(#"Mass (float): "
                       ))
    x_pos = float(input(#"Initial X position (float): \n"
                        ))
    y_pos = float(input(#"Initial Y position (float): \n"
                        ))
    z_pos = float(input(#"Initial Z position (float): \n"
                        ))
    x_vel = float(input(#"Initial X velocity (float): \n"
                        ))
    y_vel = float(input(#"Initial Y velocity (float): \n"
                        ))
    z_vel = float(input(#"Initial Z velocity (float): \n"
                        ))
    x_acc = float(input(#"Initial X acceleration (float): \n"
                        ))
    y_acc = float(input(#"Initial Y acceleration (float): \n"
                        ))
    z_acc = float(input(#"Initial Z acceleration (float): \n"
                        ))
    x_netforce = float(input(#"Initial X force (float): \n"
                             ))
    y_netforce = float(input(#"Initial Y force (float): \n"
                             ))
    z_netforce = float(input(#"Initial Z force (float): \n"
                             ))
    youngs_modulus = float(input(#"Young's modulus for material (float): \n"
                                 ))
    bulk_modulus = float(input(#"Bulk modulus for material (float): \n"
                               ))
    shear_modulus = float(input(#"Shear modulus for material (float): \n"
                                ))
    position = {
        "x": x_pos,
        "y": y_pos,
        "z": z_pos
    }
    velocity = {
        "x": x_vel,
        "y": y_vel,
        "z": z_vel
    }
    acceleration = {
        "x": x_acc,
        "y": y_acc,
        "z": z_acc
    }
    net_force = {
        "x": x_netforce,
        "y": y_netforce,
        "z": z_netforce
    }
    strain_mods = {
        "youngs": youngs_modulus,
        "bulk": bulk_modulus,
        "shear": shear_modulus
    }

    return mass, position, velocity, acceleration, net_force, strain_mods

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

class Automaton(phys.PhysicsBody): # A physics body with an associated control object
    def __init__(self, control_obj, mass, pos, vel, acc, f_n, strainmods):
        phys.PhysicsBody.__init__(self, mass, pos, vel, acc, f_n, strainmods)
        self.controller = control_obj
        self.mass = mass
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.f_n = f_n
        self.strainmods = strainmods
        self.kinematics_df = pd.DataFrame(data=[self.pos,self.vel,self.acc,self.f_n], index=["Position", "Velocity", "Acceleration", "Net Force"])
        print("Kinematics DataFrame")

        print(self.kinematics_df)

    def __str__(self):
        str_out = ("Mass: " + str(self.mass) + "\n" +
                   "Position: " + str(self.pos)+ "\n" +
                   "Velocity: " + str(self.vel) + "\n" +
                   "Acceleration: " + str(self.acc) + "\n" +
                   "Net Force: " + str(self.f_n) + "\n" +
                   "Strain Moduli: " + str(self.strainmods) + "\n")
        return str_out

class TimeAxis: # Should be a type of dataframe

    def __init__(self, initial_df): # initial_df contains sample frequency, total time, number of samples
        length_row = initial_df.iloc[2]
        length = range(length_row[0])
        dt = (1 / (initial_df.iloc[0])[0])

        self.time_axis = pd.DataFrame(index=length) # Here is a good place to add the columns, or maybe that happens in the larger modeling thing
        self.time_coords = pd.DataFrame(data=[(x * dt) for x in self.time_axis], dtype=float)

        time_index_and_vals = pd.concat([self.time_axis, self.time_coords], axis=0)


class ReferenceFrame: # This is for later, when a robot will need to use a rolling timeframe of datapoints
    def __init__(self):
        pass


class Simulation:

    def __init__(self, time_axis, physics_bodies): #physics_bodies is a list of calculated particles each with parameters
        pass

# Main Function
def main():
    sim_parameter_data = sim_parameter_getter()
    time_axis = TimeAxis(sim_parameter_data) # I don't think I've actually done anything with this yet
    ctrl1_params = pid_parameter_getter()
    controller1 = ctrl.PIDController(ctrl1_params)
    m, pos, vel, acc, f_n, strainmod = physbody_parameter_getter()
    automaton = Automaton(controller1, m, pos, vel, acc, f_n, strainmod)


    physics_bodies = [automaton]
    engine = Simulation(time_axis, physics_bodies)
    print(engine)
    print(automaton)
    return


# Main Function Call
if __name__ == "__main__":
    main()