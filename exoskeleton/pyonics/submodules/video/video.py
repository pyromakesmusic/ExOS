# Here should go video processing custom made for the exoskeleton. Most vis methods should end up in here.
import klampt
import pandas as pd
import klampt.vis as kvis
import klampt.vis.colorize


def configure_hud_vis():
    kvis.setWindowTitle("Klampt HUD  Test")
    kvis.setBackgroundColor(0, 0, 0, 1)  # Makes background black
    kvis.resizeWindow(1920, 1080)

def configure_sim_vis(vport):
    kvis.setWindowTitle("Klampt HUD  Test")
    kvis.setBackgroundColor(0.2, 0.7, 0.8, 1)  # Makes background black
    kvis.resizeWindow(1920, 1080)
    vport.fit([0, 0, -10], 65)

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
    kvis.add(name, muscle.geometry)
    kvis.setColor(name, 0, 0.2, 0, 1)
    kvis.hideLabel(name)

async def display_contact_forces(robby, sim):
    """
    Given a robot and associated simulator, lights the links of the robot according to their contact forces
    """
    links = robby.numLinks()
    for x in range(links):
        link = robby.link(x)
        simbody = sim.body(link)
        forces = sim.contactForce(simbody.getID(), -1)
        kvis.colorize.colorize(link, value="n", feature="faces", colormap="magma", lighting=forces)
    return 0
async def display_bones(robby, mask=None):
    """
    Takes robot as an argument and displays all of its bones. Uses a klampt colorize map right now.
    """
    for x in range(robby.numLinks()):
        kvis.colorize.colorize(robby.link(x), value="n", feature="faces", colormap="magma")
    return 1
def display_muscles(df=pd.DataFrame):
    """
    df: Pandas Dataframe containing muscle information.
    """
    # Should take the muscles dataframe and display them

    df.apply(display_muscle_row, axis=1)