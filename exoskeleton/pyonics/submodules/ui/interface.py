"""
LIBRARY IMPORTS
"""
# Standard Libraries
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import ipywidgets as widgets
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Third Party Libraries
import pyttsx3


# My Libraries
from exoskeleton import pyonics as modeling

"""
SYSTEM CONFIGURATION
"""

"""
FUNCTION DEFINITIONS #1 
"""
# Most of them should go here, any down after the class definitions are there only to avoid screwing things up right now

def total_num_samples_getter(sample_rate, total_time):
    total_samples = int(sample_rate * total_time)
    return total_samples


def sim_maker(sample_number):
    """
    Creates the indexed DataFrame.
    """
    headers = ["time"]
    df = pd.DataFrame(columns=headers, index=range(sample_number))
    return df


def time_samples_to_df(time_sample_df):
    """
    Turns a list of time sample coordinates into a DataFrame.
    """
    print(time_sample_df)
    values_gotten = [time_sample_df[0].get(), time_sample_df[1].get()]
    sample_number = int(total_num_samples_getter(values_gotten[0], values_gotten[1]))
    values_gotten.append(sample_number)

    for i in time_sample_df[2::1]:
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
    df = time_samples_to_df(time_series)
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


def cmdline_logic():
    user_input = "yes"
    while user_input == "yes":
        sample_freq = int(input("Sample rate in Hz (int): "))
        print(sample_freq)
        sample_length = int(input("Total time in seconds (int): "))
        print(sample_length)
        sample_number = int(total_num_samples_getter(sample_freq, sample_length))
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

        param_list = [sample_length, sample_freq, sample_number, pos_start, vel_start, accel_start,
                      mass,
                      scale_factor, set_point, p_k, i_k, d_k, control_constant]
        values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                         "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k", "control_constant"]
        initialparams = pd.DataFrame(data=param_list, index=values_labels).T
        # Need to pay attention to what this returns, this is critical for initialization
        print("Simulating . . .")
        print(".")
        print(". .")
        print(". . .")
        simdata = simulate(initialparams)
        print(simdata)
        user_input = ("Simulate again? [yes/no]: ")
    return initialparams


"""
CLASS DEFINITIONS
"""

class Interface:
    def __init__(self):
        pass

class GUI(Interface):
    def __init__(self):
        pass

class VoiceControlUI:
    def announce(self, stringvar):
        print(stringvar)
        self.voice_engine.say(stringvar)
        self.voice_engine.runAndWait()
        return

    def __init__(self):
        # TTS Engine Initialization
        self.voice_engine = pyttsx3.init()
        self.voices = self.voice_engine.getProperty("voices")
        self.voice_engine.setProperty('rate', 175)
        self.voice_engine.setProperty('voice', self.voices[1].id)

        self.recog_model = None
        self.voice_recog = None
        self.mic = None
        self.stream = None



        # This is a loop for printing voice recognized audio to the console, I think it needs to be a method or
        # attribute of how the class takes input

    def voice_recog(self):
        # Voice Recognition Initialization
        self.recog_model = vosk.Model("vosk-model-small-en-us-0.15")
        self.voice_recog = vosk.KaldiRecognizer(self.recog_model, 16000)
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=81)
        self.stream.start_stream()
        """
        while True:
            data = self.stream.read(4096)
            if self.voice_recog.AcceptWaveform(data):
                text = self.voice_recog.Result()
                print(f"{text[14:-3]}")
        """

        # Tests/ Strings

        self.voice_engine.runAndWait()
class tkinterGUI:

    def total_samples(self, sample_rate=20, total_time=20):
        total_samples = int(sample_rate * total_time)
        return total_samples

    def plot_formatter(self, df, init_df, ax):
        plt.cla()
        plot = df.plot(x="time", y="velocity", ax=self.ax)
        set_point = init_df["set_point"][0]
        lower_bound = set_point * .75
        upper_bound = set_point * 1.25
        yrange = self.ax.get_ylim()

        p = init_df["p_k"][0]
        i = init_df["i_k"][0]
        d = init_df["d_k"][0]

        p_string = "P: ".ljust(5) + str(p).rjust(10)
        i_string = "\nI: ".ljust(5) + str(i).rjust(10)
        d_string = "\nD: ".ljust(5) + str(d).rjust(10)
        txtbox = (p_string + i_string + d_string)

        properties = dict(boxstyle="square", facecolor="white", alpha=1, edgecolor="white")
        ax.yaxis.set_label_position("left")
        ax.text(.85, .5, str(txtbox), transform=self.ax.transAxes, fontsize=14,
                verticalalignment="top", bbox=properties)

        if self.display_set_point.get() == True:
            plt.axhline(y=set_point, color="r", linestyle="--")
        if self.display_overshoot_ranges.get() == True:
            plt.axhline(y=lower_bound, color="r", linestyle="--")
            plt.axhline(y=upper_bound, color="r", linestyle="--")
        if self.lock_scale.get() == True:
            self.ax.set_ylim(yrange)
            plt.yticks(np.linspace(0, 5, 10))
        plt.draw()
        return

    def list_to_df(self, list):
        values_gotten = [list[0].get(), list[1].get()]

        sample_number = int(self.total_samples(values_gotten[0], values_gotten[1]))
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
            self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=5)
            self.has_canvas = True
        elif has_figure and has_canvas:
            plt.cla()
            self.canvas.draw()
        df = simulate(init_vals_df)
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
        self.sim_and_plot(self.list_to_df(self.init_list), ax)
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
        self.sample_length = tk.IntVar()  # seconds
        self.sample_freq = tk.IntVar()  # Hz

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
        self.p_k_slider.set(0)

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
        # List of initialization parameters necessary to run the modeling
        self.init_list = [self.sample_length_slider, self.sample_freq_slider, self.position_start_slider,
                          self.velocity_start_slider,
                          self.accel_start_slider, self.mass_slider, self.scale_factor_slider, self.set_point_slider,
                          self.p_k_slider, self.i_k_slider, self.d_k_slider, self.control_constant_slider]

        # Main Button
        self.simulate_button = tk.Button(
            self.root,
            command=lambda: self.sim_and_plot(time_samples_to_df(self.init_list), self.ax),
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
            value=5
        )
        self.sample_freq_slider = widgets.IntSlider(
            min=0,
            max=10,
            step=1,
            description="Pos_0",
            value=10
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

        self.widget_list = [self.sample_length_slider, self.sample_freq_slider, self.position_start_slider,
                            self.velocity_start_slider,
                            self.accel_start_slider, self.mass_slider, self.scale_factor_slider, self.set_point_slider,
                            self.p_k_slider,
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

        self.init_list = [self.sample_length, self.sample_freq, self.sample_number, self.pos_start, self.vel_start,
                          self.accel_start, self.mass,
                          self.scale_factor, self.set_point, self.p_k, self.i_k, self.d_k, self.control_constant]


"""
FUNCTION DEFINITIONS
"""
def gui(mode):
    """
    Initialization Parameters
    """
    # Two options for GUI
    # Kinematic parameters
    if mode == "ipython":
        window = ipythonGUI()
    elif mode == "tkinter":  # the tkinter section
        window = tkinterGUI()
    return



def initialize(gui_mode="n", gui_type=None):
    """
    Starts the ui with the specified options.
    """
    if gui_mode == "y":
        gui(gui_type)
    else:
        cmdline_logic()

"""
Main Function
"""

def main():
    initialize("y", "tkinter")
    return

if __name__ == "__main__":
    main()