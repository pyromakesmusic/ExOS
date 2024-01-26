# Here should go video processing custom made for the exoskeleton. Most vis methods should end up in here.
import klampt
import pandas as pd
import klampt.vis as kvis

def configure_window():
    kvis.setWindowTitle("Klampt HUD  Test")
    kvis.setBackgroundColor(0, 0, 0, 1)  # Makes background black
    kvis.resizeWindow(1920, 1080)

def color_calc(current_pressure, max_pressure):
    # Calculates a color based on a current and max value
    if current_pressure / max_pressure < 1:
        return current_pressure / max_pressure
    else:
        return 1

def display_muscle_row(row=pd.Series):
    # Takes a dataframe row as a namedtuple and adds muscle to visualization
    print(row.index)
    print(row.info)
    name = row["name"]
    muscle = row["muscle_objects"]
    greenness = color_calc(row["pressure"], row["max_pressure"])
    kvis.add(name, muscle.geometry)
    kvis.setColor(name, 0, greenness, 0, 1)
    kvis.hideLabel(name)

def vis_muscles_beta(df=pd.DataFrame):
    # Should take the muscles dataframe and display them

    df.apply(display_muscle_row, axis=1)