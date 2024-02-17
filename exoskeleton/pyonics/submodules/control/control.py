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
import klampt.model.contact as kmc
import klampt.plan.robotplanning as kmrp
import klampt.plan.cspace as kmcs
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
    row: A single dataframe row with muscle information.
    controller: A robot controller.

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

    def collides(self):
        """
        Klampt syntactical sugar so this returns as having collision properties.
        """
        return True

    def withinDistance(self):
        """
        Same as above for shell.
        """
        return True

    def distance(self):
        """
        Same as above, returns a numeric value that is the collision distance.
        """
        return 0.8
    def update_muscle(self, pressure):  # Should call every loop?
        """
        pressure: single float value. Starting at 0-1 but may make sense to put in terms of psi, bar or pascal.
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
        force_a = kmv.mul(kmv.mul(unit_a, force), .5)  # Half (.5) because of Newton's Third Law,
        force_b = kmv.mul(kmv.mul(unit_b, force), .5)

        triplet_a = [self.b, force_a, self.transform_b]  # Should be integer, 3-tuple, transform
        triplet_b = [self.a, force_b, self.transform_a]  # Link to apply to, force vector to apply, transform at which to apply
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

class MuscleGroup():
    pass

"""
Network Controller
"""
class AsyncServer:
    """
    ip: source server ip as string
    port: client port as integer

    Server must be asynchronous to allow control loop to function intermittently.
    """
    def __init__(self, ip, port, signature_string, handler):
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
        self.password = signature_string
        self.handler = handler

    async def make_endpoint(self):
        """Need to make this endpoint"""
        assert type(self.ip) == str
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
        print("... performing mapping operation... ")
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
        self.config = config_data
        self.state = "On"
        self.shutdown_flag = False
        self.server = None
        self.collider = None

        if config_data["has_robworld"]:
            self.world = klampt.io.load('WorldModel', config_data["world_path"])  # Loads the world, this is where it's made
            self.world.loadRobot(config_data["core"])  # Loads the robot geometry
            self.robot = self.world.robot(0)
            self.interface = klampt.control.OmniRobotInterface.__init__(self, self.robot)

        self.dt = config_data["timestep"]  # Sets the core robot clock
        # Creating a series of link transforms, I need to check if this gets updated automatically
        self.bones = pd.Series([self.robot.link(x).getTransform() for x in range(self.robot.numLinks())])
        # Loading all the muscles
        self.muscles = self.muscleLoader(config_data)
        # Setting initial muscle pressure to zero
        self.pressures = [0 for x in range(len(self.muscles))]
        self.cspace = None
        self.planner = None
        asyncio.run(self.make_cspace_and_planner())  # Makes the planner

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

    """
    Kinematics and Control
    """

    def process(self, commands=None, dt=1):
        return self.set_pressures(commands)
    def sensedPosition(self):
        """
        Could still include link transforms, but should also include GPS location in lat/long, maybe USNG,
        distance from origin, pitch roll yaw, GPS, etc
        """
        return self.bones

    def set_pressures(self, *args):  # Constructed to work with an arbitrary number of values
        """
        *args: Length-n list of arguments each containing a float corresponding to some pressure.
        """
        args = list(args[2:-1])  # Removing unnecessary elements, we are getting four values now
        self.pressures = [pressure for pressure in args]
        return

    def controlRate(self):
        """
        Should be the same as the physical device, Reaktor control rate, simulation timestep
        """
        return self.dt

    async def idle_configuration(self):
        # Does the mapping and last minute settings stuff necessary to begin controller idle
        self.server = AsyncServer(self.config["address"], self.config["port"], "/pressures", self.set_pressures)
        await self.server.map("/pressures", self.set_pressures)
        await self.server.make_endpoint()

    async def idle(self, bones_transforms):
        """
        bones_transforms: A list of link locations. Essentially this is just updating the sensedPosition
        """
        self.bones = bones_transforms  # Not working quite right, might need rotation
        if self.state == "debug":
            print(self.count_muscles())
            print(self.count_bones())
        return

    async def shutdown(self):
        self.shutdown_flag = True

    """
    OPTIMIZATION
    """

    async def collision_check(self):
        """
        Low level collision checker for the robot given its loaded world.
        """
        result = kmc.world_contact_map(self.world, padding=0.1, kFriction=0.97)
        # print(x.n for x in result)
        return result

    async def make_cspace_and_planner(self):
        self.cspace = kmrp.make_space(self.world, self.robot, edgeCheckResolution=0.5)
        self.planner = kmcs.MotionPlan(self.cspace, type="prm")
        self.planner.setOptions()

    async def explore(self):
        pass

    async def close_planner(self):
        self.planner.close()

    """
    DIAGNOSTIC
    """

    async def count_muscles(self):
        return self.muscles.shape[0]

    async def count_bones(self):
        return len(self.bones)

def main():
    pass

if __name__ == "__main__":
    main()