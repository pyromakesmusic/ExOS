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

def vis_muscles(dataframe_row=pd.DataFrame):
    # Takes a dataframe row as a namedtuple and adds muscle to visualization
    name = dataframe_row.name  # Should be the name index
    print(name)
    muscle = dataframe_row.muscle_objects  # Index of the muscle object
    print(muscle)
    greenness = color_calc(muscle.pressure, muscle.max_pressure)  # Should always be less than 1s
    kvis.add(name, muscle.geometry)  # Adds the shape of the muscle - must happen
    kvis.setColor(name, 0, greenness, 0, 1)  # Sets the color of the muscle (currently green
    kvis.hideLabel(name)  # Hides the name of the muscle