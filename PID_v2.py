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

    11.3.22
    0944h
    Interface is mostly done. Needs the graph to actually be updating inside
    the GUI but otherwise the front end is ready for a presentation. Adding
    the fractional calculus functionality will be next.

===============
LIBRARY IMPORTS
===============
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
# pandas options
pd.options.display.width = 0
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# pyplot options
plt.ion()
"""
GUI Initialization
"""


"""
GLOBALS
"""
MEAN = [50,50]
COV = [
    [10,10],
    [10,10]
]
TEST_2D_DATA = np.random.multivariate_normal(MEAN, COV, 10000)

"""
PUBLIC FUNCTIONS
"""

def placeholder():
    return

"""
CLASS DEFINITIONS
"""
class tkinterGUI:
    def list_to_df(self, list):
        values_gotten = [list[0].get(), list[1].get()]

        sample_number = int(total_samples(values_gotten[0], values_gotten[1]))
        values_gotten.append(sample_number)
        for i in list[2::1]:
            values_gotten.append(i.get())
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                         "control_constant"]

        df = pd.DataFrame(data=values_gotten, index=values_labels).T
        return df
    def sim_and_plot(self, init_vals_df, ax):
        """
        This function takes the object and a dataframe as arguments and makes the plot (lots of GUI magic happening here)
        :param init_vals_df:
        :return:
        """
        df = simulate(init_vals_df)
        plot = df.plot(x="time", y="velocity", ax=ax)
        plt.draw()
        return

    def updateValue(self, event):
        if self._job:
            self.root.after_cancel(self._job)
        self._job = self.root.after(5, self.updateGraph)

    def updateGraph(self):

        """
        Here x 2 pay attention
        """
        has_graph = hasattr(self, "has_graph")
        if not has_graph:
            print(has_graph, "no graph exists yet")
            self.figure, self.ax = plt.subplots()
            figure = self.figure
            ax = self.ax
            setattr(self, "has_graph", True)
            has_graph = getattr(self, "has_graph")
            print(has_graph, "graph created")
        else:
            figure = getattr(self, "figure")
            ax = getattr(self, "ax")
            plt.cla()
        self.sim_and_plot(list_to_df(self.init_list), ax)
        return

    def __init__(self):
        self.root = tk.Tk()
        self._job = None

        self.root.title("PID Controller v1.1.b")

        self.root.attributes("-fullscreen", False)
        self.root.configure(bg="DimGray")

        """
        Simulation Parameters
        """
        # Interface flags
        self.frac_vals = tk.BooleanVar(self.root, False)
        self.lock_scale = tk.BooleanVar(self.root, False)

        # Length of dataframe variables
        self.sample_length = tk.IntVar() # seconds
        self.sample_freq = tk.IntVar() # Hz

        # Initial conditions
        self.pos_start = tk.DoubleVar()  # meters
        self.vel_start = tk.DoubleVar()  # m/s
        self.accel_start = tk.DoubleVar()  # m/s^2

        # Static variable (for now)
        self.mass = tk.DoubleVar()  # kilograms

        # PID parameters
        self.set_point = tk.DoubleVar()  # float(input("Set point of speed to maintain? "))
        self.p_k = tk.DoubleVar()  # float(input("Proportional term? "))
        self.i_k = tk.DoubleVar()  # float(input("Integral term? "))
        self.d_k = tk.DoubleVar()  # float(input("Derivative term? "))
        self.scale_factor = tk.DoubleVar()  # float(input("Scaling factor for external disturbance? "))
        self.control_constant = tk.DoubleVar()  # this is your k omega

        """
        Sliders
        """

        self.sample_length_slider = tk.Scale(
            self.root,
            from_=5,
            to=50,
            orient="horizontal",
            variable=self.sample_length,
            label="Sample Length",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.sample_freq_slider = tk.Scale(
            self.root,
            from_=5,
            to=50,
            orient="horizontal",
            variable=self.sample_freq,
            label="Sample Freq.",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        # Kinematic parameters
        self.position_start_slider = tk.Scale(
            self.root,
            from_=0,
            to=50,
            orient="horizontal",
            variable=self.pos_start,
            label="Init. Pos.",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.velocity_start_slider = tk.Scale(
            self.root,
            from_=0,
            to=50,
            orient="horizontal",
            variable=self.vel_start,
            label="Init. Vel.",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.accel_start_slider = tk.Scale(
            self.root,
            from_=0,
            to=5,
            orient="horizontal",
            variable=self.accel_start,
            label="Init. Accel",
            bg="DimGray",
            fg="White",
            command=self.updateValue)

        self.mass_slider = tk.Scale(
            self.root,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.mass,
            label="Mass",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.scale_factor_slider = tk.Scale(
            self.root,
            from_=10,
            to=1,
            resolution=.01,
            orient="vertical",
            variable=self.scale_factor,
            label="Disturbance",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        # PID parameters
        self.set_point_slider = tk.Scale(
            self.root,
            from_=50,
            to=1,
            resolution=.01,
            orient="vertical",
            variable=self.set_point,
            label="Set Point",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.p_k_slider = tk.Scale(
            self.root,
            from_=10,
            to=0,
            resolution=.01,
            orient="vertical",
            variable=self.p_k,
            label="P",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.p_k_slider.set(1)

        self.i_k_slider = tk.Scale(
            self.root,
            from_=5,
            to=-1,
            resolution=.01,
            orient="vertical",
            variable=self.i_k,
            label="I",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.i_k_slider.set(0)

        self.d_k_slider = tk.Scale(
            self.root,
            from_=5,
            to=-1,
            resolution=.01,
            orient="vertical",
            variable=self.d_k,
            label="D",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.d_k_slider.set(0)

        # Control constant
        self.control_constant_slider = tk.Scale(
            self.root,
            from_=-5,
            to=5,
            resolution=.01,
            orient="vertical",
            variable=self.control_constant,
            label="Control Const",
            bg="DimGray",
            fg="White",
            command=self.updateValue)
        self.control_constant_slider.set(1)
        # List of initialization parameters necessary to run the simulation
        self.init_list = [self.sample_length_slider, self.sample_freq_slider, self.position_start_slider, self.velocity_start_slider,
                        self.accel_start_slider, self.mass_slider, self.scale_factor_slider, self.set_point_slider,
                        self.p_k_slider, self.i_k_slider, self.d_k_slider, self.control_constant_slider]
        """
        self.figure = plt.Figure(figsize=(7,4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=5, columnspan=5)
        setattr(self, "has_graph", True)
        """

        # Main Button
        self.simulate_button = tk.Button(
            self.root,
            command=lambda: self.sim_and_plot(list_to_df(self.init_list)),
            text="Simulate",
            bg="silver",
            fg="Black")

        self.clear_plot = tk.Button(self.root,
                                    command=plt.cla,
                                    text="Clear Plot",
                                    bg="DimGray",
                                    fg="White")

        self.save_plot = tk.Button(self.root,
                                   text="Save Plot",
                                   bg="DimGray",
                                   fg="White")



        # Additional Check Options
        self.lock_scale_check = tk.Checkbutton(self.root,
                                    text="Lock Scale",
                                    bg="DimGrey",
                                    fg="Black",
                                    onvalue=True,
                                    variable=self.lock_scale)
        self.frac_vals_check = tk.Checkbutton(self.root,
                                        text="Fractional PID",
                                        bg="DimGrey",
                                        fg="Black",
                                        onvalue=True,
                                        variable=self.frac_vals)

        self.save_plot.grid(row=0, column=0)
        self.clear_plot.grid(row=1, column=0)
        self.simulate_button.grid(row=2, column=0)


        self.frac_vals_check.grid(row=0, column=5)
        self.lock_scale_check.grid(row=1, column=5)

        # Initialization Params
        self.sample_length_slider.grid(row=0, column=1, sticky="nsew")
        self.sample_freq_slider.grid(row=1, column=1, sticky="nsew")
        self.position_start_slider.grid(row=0, column=2, sticky="nsew")
        self.velocity_start_slider.grid(row=1, column=2, sticky="nsew")
        self.accel_start_slider.grid(row=2, column=2, sticky="nsew")
        self.mass_slider.grid(row=2, column=1, sticky="nsew")

        # PID Params
        self.scale_factor_slider.grid(row=0, column=3, sticky="nsew")
        self.set_point_slider.grid(row=0, column=4, sticky="nsew")

        self.p_k_slider.grid(row=1, column=3, sticky="nsew")
        self.i_k_slider.grid(row=1, column=4, sticky="nsew")

        self.d_k_slider.grid(row=2, column=3, sticky="nsew")
        self.control_constant_slider.grid(row=2, column=4, sticky="nsew")


        self.root.mainloop()

class ipythonGUI:

    def ipython_list_to_df(self, list):
        values_gotten = [list[0], list[1]]

        sample_number = int(total_samples(values_gotten[0], values_gotten[1]))
        values_gotten.append(sample_number)
        for i in list[2::1]:
            values_gotten.append(i)
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                         "control_constant"]

        df = pd.DataFrame(data=values_gotten, index=values_labels).T
        return df
    def sim_and_plot(self, init_vals_df, axes):
        df = simulate(init_vals_df)
        df.plot(x="time", y="velocity", ax=axes)
        plt.draw()
        return

    def __init__(self):
        self.sample_length_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )
        self.sample_freq_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )
        self.position_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )

        self.velocity_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Vel_0",
            value=0
        )

        self.accel_start_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Accel_0",
            value=0
        )

        self.mass_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=0
        )

        self.scale_factor_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Dist Factor",
            value=0
        )

        # PID parameters

        self.set_point_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Set Point",
            value=0
        )

        self.p_k_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="P_K",
            value=0
        )

        self.i_k_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="I_K",
            value=0
        )

        self.d_k_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="D_K",
            value=0
        )

        # Control constant
        self.control_constant_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Ctrl Const",
            value=0
        )

        self.widget_list = [self.sample_length_slider, self.sample_freq_slider, self.position_start_slider, self.velocity_start_slider,
                            self.accel_start_slider, self.mass_slider, self.scale_factor_slider, self.set_point_slider, self.p_k_slider,
                            self.i_k_slider, self.d_k_slider, self.control_constant_slider]
        for item in self.widget_list:
            display(item)

        self.sample_length = self.sample_length_slider.value
        self.sample_freq = self.sample_freq_slider.value
        self.pos_start = self.position_start_slider.value
        self.vel_start = self.velocity_start_slider.value
        self.accel_start = self.accel_start_slider.value

        self.mass = self.mass_slider.value
        self.scale_factor = self.scale_factor_slider.value
        self.set_point = self.set_point_slider.value
        self.p_k = self.p_k_slider.value
        self.i_k = self.i_k_slider.value
        self.d_k = self.d_k_slider.value
        self.control_constant = self.control_constant_slider.value
        self.sample_number = int(total_samples(self.sample_freq, self.sample_length))
        self.init_list = [self.sample_length, self.sample_freq, self.sample_number, self.pos_start, self.vel_start,
                                    self.accel_start, self.mass, self.scale_factor, self.set_point, self.p_k, self.i_k, self.d_k,
                                    self.control_constant]

        self.figure = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.simulate_button = widgets.Button(
            description="Simulate",
            icon="play")

        self.simulate_button.on_click(self.sim_and_plot(self.ipython_list_to_df(self.init_list), self.ax))

        self.ax.set_title('Velocity vs. Time')

        self.widget_list = [self.sample_length_slider, self.sample_freq_slider, self.position_start_slider,
                            self.velocity_start_slider,
                            self.accel_start_slider, self.mass_slider, self.scale_factor_slider, self.set_point_slider,
                            self.p_k_slider,
                            self.i_k_slider, self.d_k_slider, self.control_constant_slider, self.simulate_button]

        for item in self.widget_list:
            display(item)

        self.init_list = [self.sample_length, self.sample_freq, self.sample_number, self.pos_start, self.vel_start, self.accel_start, self.mass,
                               self.scale_factor, self.set_point, self.p_k, self.i_k, self.d_k, self.control_constant]
"""
FUNCTION DEFINITIONS
====================
"""


def total_samples(sample_rate=20, total_time=20):
    total_samples = int(sample_rate * total_time)
    return total_samples


def row_maker(total_samples):
    """
    Creates the indexed DataFrame.
    :param total_samples:
    :param smp_rate:
    :return:
    """
    headers = ["time","mass", "disturbance_force", "error", "proportional", "integral", "derivative", "pid", "throttle_force", "total_force", "acceleration", "velocity", "position"]
    df = pd.DataFrame(columns=headers, index=range(total_samples))
    return df

def list_to_df(list):
    values_gotten = [list[0].get(), list[1].get()]

    sample_number = int(total_samples(values_gotten[0], values_gotten[1]))
    values_gotten.append(sample_number)
    for i in list[2::1]:
        values_gotten.append(i.get())
    values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                     "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                     "control_constant"]

    df = pd.DataFrame(data=values_gotten, index=values_labels).T
    return df

def cmdline_logic():
    user_input = input("Simulate? [yes/no]: ")
    while user_input == "yes":
        sample_freq = int(input("Sample rate in Hz (int): "))
        print(sample_freq)
        sample_length = int(input("Total time in seconds (int): "))
        print(sample_length)
        sample_number = int(total_samples(sample_freq, sample_length))
        print("Total number of samples:", sample_number)
        set_point = float(input("Set point for cruise control (float): "))
        print(set_point)
        pos_start = float(input("Start position (float): "))
        print(pos_start)
        vel_start = float(input("Start velocity (float): "))
        print(vel_start)
        accel_start = float(input("Start acceleration (float): "))
        print(accel_start)

        mass = float(input("Mass (float): "))
        print(mass)
        scale_factor = float(input("Scaling factor for external disturbance (float): "))
        print(scale_factor)
        p_k = float(input("Proportional scaling factor (float): "))
        print(p_k)
        i_k = float(input("Integral scaling factor (float): "))
        print(i_k)
        d_k = float(input("Derivative scaling factor (float): "))
        print(d_k)
        control_constant = float(input("Constant multiple for PID term to throttle output (float): "))
        print(control_constant)
        control_sign = int(input("Sign of throttle vs. PID: "))
        print(control_sign)

        param_list = [sample_length, sample_freq, sample_number, pos_start, vel_start, accel_start,
                      mass,
                      scale_factor, set_point, p_k, i_k, d_k, control_constant, control_sign]
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k", "control_constant", "control_sign"]
        initialparams = pd.DataFrame(data=param_list, index=values_labels).T
        # Need to pay attention to what this returns, this is critical for initialization
        print("Simulating . . .")
        print(".")
        print(". .")
        print(". . .")
        simulation = simulate(initialparams)
        print(simulation)
        user_input = ("Simulate again? [yes/no]: ")
    return initialparams

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
    time_series = row_maker(sample_number)
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
        df = pid(df, x, p_k, i_k, d_k, control_const)
    graph = plt.plot(df["time"], df["velocity"])
    plt.draw()
    return df


def sim_and_plot(init_vals_df, ax):
    simulate(init_vals_df).plot(x="time", y="velocity", ax=ax)
    return
def gui(mode):

    """
    Initialization Parameters
    """
    # Two options for GUI
    # Kinematic parameters
    if mode == "ipython":
        window = ipythonGUI()
    elif mode == "tkinter": # the tkinter section
        window = tkinterGUI()
    return

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
        derivative = d_k * df.at[i, "error"]
    pid = scaling_factor * (proportional + integral + derivative)
    df.at[i, "proportional"] = proportional
    df.at[i, "integral"] = integral
    df.at[i, "derivative"] = derivative
    df.at[i, "pid"] = pid
#    print("P:",proportional," I:", integral," D:", derivative," PID:", pid)
    return df

def main():
    initialize()
    return

main()