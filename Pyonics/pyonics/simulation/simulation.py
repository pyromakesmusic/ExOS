
def total_samples(sample_rate=20, total_time=20):
    total_samples = int(sample_rate * total_time)
    return total_samples


def row_maker(sample_num):
    """
    Creates the indexed DataFrame.
    :param total_samples:
    :param smp_rate:
    :return:
    """
    headers = ["time", "mass", "disturbance_force", "error", "proportional", "integral", "derivative", "control",
               "throttle_force", "total_force", "acceleration", "velocity", "position"]
    df = pd.DataFrame(columns=headers, index=range(sample_num))
    return df


def list_to_df(listy):
    """
    Turns a list of time sample coordinates into a DataFrame.
    """
    values_gotten = [listy[0].get(), listy[1].get()]

    sample_number = int(total_samples(values_gotten[0], values_gotten[1]))
    values_gotten.append(sample_number)
    for i in listy[2::1]:
        values_gotten.append(i.get())
    values_labels = ["sample_length", "sample_freq", "sample_number", "pos_start", "vel_start", "accel_start",
                     "mass", "scale_factor", "set_point", "p_k", "i_k", "d_k",
                     "control_constant"]

    df = pd.DataFrame(data=values_gotten, index=values_labels).T
    return df
