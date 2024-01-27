"""
DEVELOPER COMMENTS

Keep at bottom level, so no references to other user-created libraries. Low level control algorithms. Probably best
to optimize with C/C++.
"""

"""
STANDARD LIBRARY IMPORTS
"""
import pandas as pd
import numpy as np
import argparse
import asyncio
import math

"""
OUTSIDE LIBRARY IMPORTS
"""
import klampt
import klampt.math.vectorops as kmv
import pythonosc
from pythonosc.dispatcher import Dispatcher
import pythonosc.osc_server

"""
CUSTOM LIBRARY IMPORTS
"""

"""
CLASS DEFINITIONS
"""
"""
Hardware
"""
class Muscle(klampt.sim.ActuatorEmulator):
    """
    Refers to exactly one McKibben muscle, with all associated attributes.
    This may end up being an interface for both an Actuator and a simulated ActuatorEmulator, running simultaneously.
    """
    def __init__(self, row, controller):
        """
        Takes a dataframe row containing muscle information, a world model, a simulator, and a controller.
        """
        klampt.sim.ActuatorEmulator.__init__(self)
        self.controller = controller
        self.a = int(row["link_a"])  # Gets index of the row of link a
        self.b = int(row["link_b"])

        self.link_a = self.controller.bones[self.a]  # Refers to the **controller's** knowledge of the link *transform*
        self.link_b = self.controller.bones[self.b]  # Might need to be updated
        """
        The below values describe the displacement of the muscle attachment from the origin of the robot link.
        """
        self.delta_a = [float(s) for s in row["transform_a"].split(",")]
        self.delta_b = [float(s) for s in row["transform_b"].split(",")]

        # This starts out fine, but may eventually need to be updated each time step according to link position
        self.transform_a = kmv.add(self.link_a[1], self.delta_a)
        self.transform_b = kmv.add(self.link_b[1], self.delta_b)

        # Now we add some attributes that the simulated and real robot will share
        self.geometry = klampt.GeometricPrimitive()
        self.geometry.setSegment(self.transform_a, self.transform_b)

        self.turns = row["turns"]  # Number of turns in the muscle fiber
        self.weave_length = row["weave_length"]  # weave length - should be shorter than l_0
        self.max_pressure = row["max_pressure"]  # want this to autoscale for now, eventually static
        self.r_0 = row["r_0"]  # resting radius - at nominal relative pressure
        self.l_0 = row["l_0"]  # resting length - at nominal relative pressure
        self.length = self.l_0  # For calculation convenience. self.length should change eache time step
        self.displacement = 0  # This is a calculated value; should initialize at 0
        self.pressure = 0  # Should be pressure relative to external, so initialize at 0 - need units eventually

    def update(self, pressure): # Should call every loop?
        """
        ================
        UPDATE 10.2.2023: A muscle is a spring with variable stiffness.

        Should apply two forces at points determined by self.transform_a and self.transform_b, moderated by the
        McKibben muscle formula.

        We want to calculate
        F: the force applied by the muscle.
        To do this we will need:
        p: relative pressure of the air chamber
        b: the muscle fiber weave length
        n: number of turns in the muscle fiber
        x: the displacement. This will probably take the most work to calculate.
        """
        # Muscle transforms must update based on new link positions //// maybe not with applyForceAtLocalPoint()
        self.link_a = self.controller.bones[self.a]
        self.link_b = self.controller.bones[self.b]

        self.transform_a = kmv.add(self.link_a[1], self.delta_a)  # Adds link transform to muscle delta
        self.transform_b = kmv.add(self.link_b[1], self.delta_b)

        self.geometry.setSegment(self.transform_a, self.transform_b)  # Should be updating the transform

        self.pressure = pressure  # Updates muscle pressure
        self.length = kmv.distance(self.transform_a, self.transform_b)
        self.displacement = self.length - self.l_0  # Calculates displacement based on new length

        # Muscle formula
        force = ((self.pressure * (self.weave_length)**2)/(4 * math.pi * (self.turns)**2)) * \
                (((self.weave_length)/math.sqrt(3) + self.displacement)**2 - 1)

        # Calculating a 3-tuple that gives a direction
        direction_a = kmv.sub(self.transform_a, self.transform_b)
        direction_b = kmv.mul(direction_a, -1) # Should just be the reverse of direction_a

        # Calculating unit vectors by dividing 3-tuple by its length
        unit_a = kmv.div(direction_a, self.length)
        unit_b = kmv.mul(direction_b, self.length)  # Redundant but I'm including this to make it easier to read for now

        # Combining unit vectors and force magnitude to give a force vector
        force_a = kmv.mul(kmv.mul(unit_a, force), 5)  # Half (.5) because of Newton's Third Law,
        force_b = kmv.mul(kmv.mul(unit_b, force), 5)

        triplet_a = [self.b, force_a, self.transform_b]  # Should be integer, 3-tuple, transform
        triplet_b = [self.a, force_b, self.transform_a]
        """
        These triplets are what is required to simulate the effect of the muscle contraction. Also, at some point I want
        to change the muscle color based on the pressure input.
        """
        return triplet_a, triplet_b

    def pressure_autoscale(self):
        if self.pressure > self.max_pressure:  # autoscaling algorithm
            self.max_pressure = self.pressure

    def appearance(self):
        app = klampt.Appearance()
        app.setDraw(2, True)
        app.setColor(0, 1, 0, 1)
        return app


"""
Network Controller
"""
class AsyncServer:
    """
    Server must be asynchronous to allow control loop to function intermittently.
    """
    def __init__(self, ip, port):
        self.dispatcher = pythonosc.dispatcher.Dispatcher()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--ip", default=ip, help="The IP address to listen on")
        self.parser.add_argument("--port", type=int, default=port, help="The port to listen on")
        self.args = self.parser.parse_args()
        self.ip = ip
        self.port = port
        self.server = None
        self.transport = None
        self.protocol = None

    async def make_endpoint(self):
        "Need to make this endpoint"
        self.server = pythonosc.osc_server.AsyncIOOSCUDPServer((self.ip, self.port),
                                                               self.dispatcher, asyncio.get_running_loop())
        self.transport, self.protocol = await self.server.create_serve_endpoint()
        print("Serving on {}".format(self.ip))
        return

    async def map(self, pattern, func, *args, **kwargs):
        """
        pattern: string var defining the OSC pattern to be recognized
        func: the function to map to
        args: any args for the function, this may need to be *args and **kwargs - needs more research
        """
        self.dispatcher.map(pattern, func, args)


"""
Robot Controller
"""
class ExoController(klampt.control.OmniRobotInterface):
    """
    Most low level hardware controller. No display, but contains enough of a world to start generating HUD elements.
    """

    # Initialization
    def __init__(self, config_data):
        """
        Initializes the controller. Should work on a physical or simulated robot equivalently or simultaneously.
        """
        # print(config_data)
        self.shutdown_flag = False
        self.input = None

        if config_data["has_robworld"]:
            # print(". . . c r e a t i n g w o r l d . . .")
            self.world = klampt.io.load('WorldModel', config_data["world_path"])  # Loads the world, this is where it's made
            self.world.loadRobot(config_data["core"])  # Loads the robot geometry
            self.robot = self.world.robot(0)
            # print("this is the robot")
            self.interface = klampt.control.OmniRobotInterface.__init__(self, self.robot)


        self.dt = config_data["timestep"]  # Sets the core robot clock
        self.osc_server = AsyncServer(config_data["address"], config_data["port"])
        self.oscMapper()
        # Creating a series of link transforms, I need to check if this gets updated automatically
        self.bones = pd.Series([self.robot.link(x).getTransform() for x in range(self.robot.numLinks())])
        # Loading all the muscles
        self.muscles = self.muscleLoader(config_data)
        # Setting initial muscle pressure to zero
        self.pressures = [0.5 for x in range(len(self.muscles))]
        # print(". . . r e t u r n i n g r o b o t. . . ")

    def muscleLoader(self, config_df):
        """
        Given a dataframe with an ["attachments"] column containing a path
        to a .csv file detailing structured muscle parameters, generates a list of Muscle objects and
        assigns them to the robot model. This should generate all muscles.
        """
        with open(config_df["attachments"]) as attachments:
            muscleinfo_df = pd.read_csv(attachments, sep=";")  # This dataframe contains info on every muscle attachment
            rows = muscleinfo_df.shape[0]  # This is the number of rows, so the while loop should loop "row" many times

            muscle_objects = []  # Placeholder list, made to be empty and populated with all muscle objects.

            for x in range(rows):
                row = muscleinfo_df.iloc[x] # Locates the muscle information in the dataframe
                muscle = Muscle(row, self) # Calls the muscle class constructor
                muscle_objects.append(muscle) # Adds the muscle to the list

            muscle_series = pd.Series(data=muscle_objects, name="muscle_objects")
            pressure_series = pd.Series(data=0, name="pressure")
            muscleinfo_df = pd.concat([muscleinfo_df, muscle_series, pressure_series], axis=1)

            """
            This dataframe should end with all the info in the muscle attachments CSV, plus corresponding muscle objects
            in each row.
            # """
            # print(str(muscleinfo_df) + " muscleinfo df") # Doing test prints
            return muscleinfo_df

    # Control and Kinematics

    def oscMapper(self):
        """
        Sets up the OSC control inputs.
        """
        print("mapping OSC signature to function...")
        self.osc_server.map("/pressures", self.setPressures)
        return
    def sensedPosition(self):
        """
        Could still include link transforms, but should also include GPS location in lat/long, maybe USNG,
        distance from origin, pitch roll yaw, GPS, etc
        """
        return self.bones

    async def setPressures(self, *args):  # Constructed to work with an arbitrary number of values
        print("setting pressure...")
        print(args)
        args = list(args[2:-1])  # Removing unnecessary elements, we are getting four values now
        self.pressures = [pressure for pressure in args]
        return

    def validateInput(self, stringvar):
        if stringvar == None:
            return ""
        else:
            return stringvar

    def controlRate(self):
        """
        Should be the same as the physical device, Reaktor control rate, simulation timestep
        """
        return self.dt

    async def beginIdle(self):
        """
        Used for loops.
        """
        self.shutdown_flag = False
        await (self.osc_server.make_endpoint())
        while not self.shutdown_flag:
            await self.idle()

    async def idle(self, bones_transforms):
        """
        bones_transforms: A list of link locations
        """
        self.setPressures()
        print("self.pressures: \n")
        print(self.pressures)
        # self.input = input  # Runs the voice assistant at idle to get input
        self.bones = bones_transforms  # Not working quite right, might need rotation
        force_list = []  # Makes a new empty list... of tuples? Needs link number, force, and transform
        i = 0
        for muscle in self.muscles.muscle_objects:
            print(str(muscle) + "is the muscle")
            triplet_a, triplet_b = muscle.update(self.pressures[i])  # Updates muscles w/ OSC argument
            force_list.append(triplet_a)
            force_list.append(triplet_b)
            i += 1
        # print(pd.Series(force_list))
        await asyncio.sleep(1)
        force_series = pd.Series(force_list)
        # print("These are the forces " + str(force_series))
        return pd.Series(force_list)

    def shutdown(self):
        self.shutdown_flag = True




"""
FUNCTION DEFINITIONS
"""



def error(set_point, df, i):
    """
    Determines the error between a set point and a current value ( stored in a dataframe with i+2 steps)
    :param process_variable:
    :param set_point:
    :param df: main dataframe
    :param i: time step
    :return: modified dataframe
    """
    error = set_point - df.at[i, "velocity"]
    df.at[i, "error"] = error
    return df

def pid(df, i, p_k, i_k, d_k, scaling_factor):
    """
    Performs the PID logic.
    :param df: main dataframe
    :param i: time step
    :param p_k: proportional value
    :param i_k: integral control value
    :param d_k: derivative control value
    :scaling_factor: factor to scale all three of P, I and D to before final output
    :return: modified dataframe
    """
    df_abridged = df[0:i]
    proportional = p_k * df.at[i, "error"] # Some constant times the error
    integral = i_k * np.trapz(df_abridged["error"]) # Trapezoid rule for discrete integral
    if i < 2:
        derivative = 0
    else:
        gradient = np.gradient(df_abridged["error"])
        derivative = d_k * float(gradient[-2:-1])
    pid = scaling_factor * (proportional + integral + derivative)
    df.at[i, "proportional"] = proportional
    df.at[i, "integral"] = integral
    df.at[i, "derivative"] = derivative
    df.at[i, "control"] = pid
    return df

"""
MAIN FUNCTION CALL
"""

def main():
    pass

if __name__ == "__main__":
    main()