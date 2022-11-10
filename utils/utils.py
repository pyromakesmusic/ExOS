import pandas as pd


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