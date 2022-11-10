from gui import ipython_view, tkinter_view
from utils import utils


def gui(mode):

    """
    Initialization Parameters
    """
    # Two options for GUI
    # Kinematic parameters
    if mode == "ipython":
        window = ipython_view.ipythonGUI()
    elif mode == "tkinter": # the tkinter section
        window = tkinter_view.tkinterGUI()
    return


def cmdline_logic():
    user_input = input("Simulate? [yes/no]: ")
    while user_input == "yes":
        sample_freq = int(input("Sample rate in Hz (int): "))
        print(sample_freq)
        sample_length = int(input("Total time in seconds (int): "))
        print(sample_length)
        sample_number = int(utils.total_samples(sample_freq, sample_length))
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