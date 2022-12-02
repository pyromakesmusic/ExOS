"""
LIBRARY IMPORTS
"""
import sys
import numpy as np
import pandas as pd
import physics
import control

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


class PhysicsSim(Simulation):
    def __init__(self):
        return
    pass


"""
FUNCTION DEFINITIONS
"""


def main():
    return


if __name__ == "__main__":
    main()