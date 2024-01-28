# Here should go video processing custom made for the exoskeleton. Most vis methods should end up in here.
import klampt
import pandas as pd
import klampt.vis as kvis


def configure_hud_vis():
    kvis.setWindowTitle("Klampt HUD  Test")
    kvis.setBackgroundColor(0, 0, 0, 1)  # Makes background black
    kvis.resizeWindow(1920, 1080)

def configure_sim_vis():
    kvis.setWindowTitle("Klampt HUD  Test")
    kvis.setBackgroundColor(0.3, 0, 0.5, 1)  # Makes background black
    kvis.resizeWindow(1920, 1080)

def color_calc(current_pressure, max_pressure):
    # Calculates a color based on a current and max value
    if current_pressure / max_pressure < 1:
        return current_pressure / max_pressure
    else:
        return 1

def display_muscle_row(row=pd.Series):
    """
    row: Pandas DataFrame row (as a Pandas Series) containing muscle information.
    """
    # Takes a dataframe row as a namedtuple and adds muscle to visualization
    # print(row.index)
    # print(row.info)
    name = row["name"]
    muscle = row["muscle_objects"]
    redness = color_calc(row["pressure"], row["max_pressure"])
    greenness = 1 - redness
    # print(str(redness) + " is the redness")
    kvis.add(name, muscle.geometry)
    kvis.setColor(name, redness, greenness, 0, 1)
    kvis.hideLabel(name)

def display_muscles(df=pd.DataFrame):
    """
    df: Pandas Dataframe containing muscle information.
    """
    # Should take the muscles dataframe and display them

    df.apply(display_muscle_row, axis=1)