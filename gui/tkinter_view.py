import tkinter as tk
from tkinter import ttk
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ipywidgets as widgets
from IPython.display import display
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from utils import utils
from control_flow import control


class tkinterGUI:

    def plot_formatter(self, df, init_df, ax):
        plt.cla()
        plot = df.plot(x="time", y="velocity", ax=self.ax)
        plt.draw()
        return

    def list_to_df(self, list):
        values_gotten = [list[0].get(), list[1].get()]

        sample_number = int(utils.total_samples(values_gotten[0], values_gotten[1]))
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
        has_figure = hasattr(self, "figure")
        has_ax = hasattr(self, "ax")
        has_canvas = hasattr(self, "canvas")
        if has_figure and not has_canvas:
            self.canvas = FigureCanvasTkAgg(self.figure, self.root)
            plt.cla()
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=5,column=0,columnspan=5)
            self.has_canvas = True
        elif has_figure and has_canvas:
            plt.cla()
            self.canvas.draw()
        df = control.simulate(init_vals_df)
        self.plot_formatter(df, init_vals_df, self.ax)
        return

    def updateValue(self, event):
        if self._job:
            self.root.after_cancel(self._job)
        self._job = self.root.after(50, self.updateGraph)

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
        self.sim_and_plot(utils.list_to_df(self.init_list), ax)
        return

    def __init__(self):
        self.root = tk.Tk()
        self._job = None

        self.root.title("PID Controller v1.2.b")

        self.root.attributes("-fullscreen", False)
        self.root.configure(bg="DimGray")

        """
        Simulation Parameters
        """
        # Interface flags
        self.frac_vals = tk.BooleanVar(self.root, False)
        self.lock_scale = tk.BooleanVar(self.root, False)
        self.display_set_point = tk.BooleanVar(self.root, False)
        self.display_overshoot_ranges = tk.BooleanVar(self.root, False)

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
            from_=9,
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
            from_=3,
            to=0,
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
            from_=3,
            to=0,
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
            from_=5,
            to=-1,
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

        # Main Button
        self.simulate_button = tk.Button(
            self.root,
            command=lambda: self.sim_and_plot(utils.list_to_df(self.init_list)),
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
        self.set_point_check = tk.Checkbutton(self.root,
                                    text="Show Set Point",
                                    bg="DimGrey",
                                    fg="Black",
                                    onvalue=True,
                                    variable=self.display_set_point)
        self.overshoot_ranges_check = tk.Checkbutton(self.root,
                                        text="Show 25% Ranges",
                                        bg="DimGrey",
                                        fg="Black",
                                        onvalue=True,
                                        variable=self.display_overshoot_ranges)

        self.save_plot.grid(row=0, column=0)
        self.clear_plot.grid(row=1, column=0)
        self.simulate_button.grid(row=2, column=0)

        self.frac_vals_check.grid(row=0, column=5, sticky="w")
        self.lock_scale_check.grid(row=1, column=5, sticky="w")
        self.set_point_check.grid(row=2, column=5, sticky="w")
        self.overshoot_ranges_check.grid(row=3, column=5, sticky="w")
        # i term order
        # d term order

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