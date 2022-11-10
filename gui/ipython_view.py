import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ipywidgets as widgets
from IPython.display import display
import numpy as np
import pandas as pd
import math
import matplotlib as mpl
import matplotlib.pyplot as plt

from utils import utils
from control_flow import control


class ipythonGUI:

    def ipython_list_to_df(self, list):
        values_gotten = [list[0], list[1]]

        sample_number = int(utils.total_samples(values_gotten[0], values_gotten[1]))
        values_gotten.append(sample_number)
        for i in list[2::1]:
            values_gotten.append(i)
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                         "control_constant"]

        df = pd.DataFrame(data=values_gotten, index=values_labels).T
        return df
    def sim_and_plot(self, init_vals_df, axes):
        df = control.simulate(init_vals_df)
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
        self.sample_number = int(utikls.total_samples(self.sample_freq, self.sample_length))
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