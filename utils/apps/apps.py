import asyncio  # Needs asynchronous functionality
import pandas as pd
import gpsd  # GPS library
# import cv2  # CameraWidget library
from datetime import datetime
import asyncio
# Klamp't imports

import klampt
import klampt.model.coordinates
import klampt.model.collide
import klampt.model.contact
import klampt.plan.robotplanning
import klampt.plan.robotcspace
import klampt.plan.cspace
import klampt.plan.rigidobjectcspace

# Each app should be its own class
from pyonics import MuscleEmulator

"""
CLASSES
"""

# HUD Widgets
class Map(klampt.vis.glcommon.GLProgram):
    def __init__(self, widget=None):
        self.world = klampt.WorldModel()
        self.frenet = klampt.model.coordinates.Frame("frenet frame", self.world)
        self.latitude = None
        self.longitude = None
        self.altitude = None

        self.bearing = "east"
        self.widget = widget
        self.get_gps_data()
        klampt.vis.glprogram.GLProgram.__init__(self)

    async def surrounding_geometry(self):
        pass


    def get_gps_data(self):
        # Connect to the local gpsd service (default host and port)
        try:
            gpsd.connect()
            # Get the GPS data
            packet = gpsd.get_current()
            # Check if the data is valid
            if packet.mode >= 2:
                self.latitude = packet.lat
                self.longitude = packet.lon
                self.altitude = packet.alt

                return (f"Latitude: {self.latitude},\n Longitude: {self.longitude},\n Altitude: {self.altitude}")
            else:
                return ("No GPS fix")
        except ConnectionRefusedError:

            return("GPS Fix failed")

    def update(self, bearing):
        gpsd.connect()
        # Get the GPS data
        packet = gpsd.get_current()
        # Check if the data is valid
        if packet.mode >= 2:
            self.latitude = packet.lat
            self.longitude = packet.lon
            self.altitude = packet.alt

        self.bearing = bearing

    def set_widget(self, widget):
        self.widget = widget

class Clock():
    def __init__(self, widget=None, widget_type=None):
        # Adds a clock
        self.time = datetime.now().strftime("%H:%M:%S")
        self.widget = widget
        self.widget_type = widget_type
    def update(self):
        self.time = datetime.now().strftime("%H:%M:%S")
        return self.time

    def set_widget(self, widget, widget_type):
        self.widget = widget
        self.widget_type = widget_type

class DateWidget:
    def __init__(self):
        # Adds a clock
        self.date = datetime.now().strftime("%Y.%m.%d")
        self.display = None
    def update(self):
        self.date = datetime.now().strftime("%Y.%m.%d")
        return self.date

class TextWidget:
    def __init__(self):
        # Adds a clock
        self.text = "widget text"
    def update(self, text):
        self.text = text
        return self.text

# class CameraWidget(klampt.vis.glcommon.GLProgram):
#     def __init__(self, i):
#         klampt.vis.glcommon.GLProgram.__init__(self)
#         # Launches with an index of a particular camera
#         self.camera = None
#         self.state = "minimized"  # Can also be "fullscreen", "windowed", "closed"
#
#         self.ret = None
#         self.frame = None
#         self.shutdown_flag = False
#
#
#
#
#     def cam_launch(self, index):
#         # Start the camera
#         try:
#             self.camera = cv2.VideoCapture(index)
#         except:
#             "Error: Exception launching camera input."
#
#         while not self.shutdown_flag:
#             asyncio.run(self.cam_loop())
#
#     def cam_loop_synchronous(self):
#         self.ret, self.frame = self.camera.read()
#
#         # Check if the frame was read successfully
#         if not self.ret:
#             print("Error: Could not read frame.")
#
#         # Display the frame
#         cv2.imshow('Webcam', self.frame)
#         return self.frame
#
#     async def cam_loop(self):
#         self.ret, self.frame = self.camera.read()
#
#         # Check if the frame was read successfully
#         if not self.ret:
#             print("Error: Could not read frame.")
#
#
#         # Display the frame
#         cv2.imshow('Webcam', self.frame)
#         return self.frame
#
#     def cam_shutdown(self):
#         # Break the loop if the user presses the 'q' key
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             self.shutdown_flag = True

# Desktop Applications

"""
Simulation
"""
class Sim(klampt.sim.simulation.SimpleSimulator):
    """
    This is a class for Simulations. It will contain the substepping logic where forces are applied to simulated objects.
    """
    def __init__(self, wm, pcm, timestep, config_df, collisions=True):  # Setting collisions to True for testing ONLY
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.world = wm
        self.dt = timestep
        self.pcm = pcm
        self.robotmodel = self.pcm.robot
        self.config = config_df

        # self.reset() # Testing this to see if it helps reset the simulated robot config in ODESimulator

        q = self.robotmodel.getConfig()
        self.robotmodel.setConfig(q)
        self.robotmodel.setVelocity([0.0] * len(q))

        if collisions:
            self.collider = klampt.model.collide.WorldCollider(self.world)
            self.planner = klampt.plan
        else:
            self.collider = None

        self.muscles = None
        self.muscleLoader(self.config)

    def muscleLoader(self, config_df):
        """
        Given a dataframe with an ["attachments"] column containing a path
        to a .csv file detailing structured muscle parameters, generates a list of MuscleEmulator objects and
        assigns them to the robot model. This should generate all muscles.
        """
        with open(config_df["attachments"]) as attachments:
            muscleinfo_df = pd.read_csv(attachments, sep=";")  # This dataframe contains info on every muscle attachment
            rows = muscleinfo_df.shape[0]  # This is the number of rows, so the while loop should loop "row" many times

            muscle_objects = []  # Placeholder list, made to be empty and populated with all muscle objects.

            for x in range(rows):
                row = muscleinfo_df.iloc[x] # Locates the muscle information in the dataframe
                muscle = MuscleEmulator(row, self.pcm, self) # Calls the muscle class constructor, has robot controller as argument
                muscle_objects.append(muscle) # Adds the muscle to the list

            muscle_series = pd.Series(data=muscle_objects, name="muscle_objects")
            pressure_series = pd.Series(data=[0] * len(muscle_series), name="pressure")
            self.muscles = pd.concat([muscleinfo_df, muscle_series, pressure_series], axis=1)
            print(self.muscles)
            for muscle in self.muscles["muscle_objects"]:
                self.addEmulator(self.robotmodel, muscle)
            return
    async def simLoop(self):
        """
        robot: A RobotModel.
        force_list: Not sure what data structure, maybe a dataframe? name of muscle as index, with force and transform
        """
        self.pcm.set_pressures
        self.simulate(self.dt)
        self.updateWorld()
        return

    async def testSimLoop(self):
        """
        robot: A RobotModel.
        force_list: Not sure what data structure, maybe a dataframe? name of muscle as index, with force and transform

        Should possibly return a list of new transforms to be used for calculating stuff in the next time step.

        """
        self.simulate(self.dt) # Same as the controller update
        self.updateWorld()
        return

    async def configure_sim(self):
        """
        Sets up the simulation to do whatever I want it to do.
        """
        self.setSetting("boundaryLayerCollisions", "1")
        self.setSetting("rigidObjectCollisions", "1")
        self.setSetting("robotSelfCollisions", "1")
        self.setSetting("robotRobotCollisions", "1")
        self.setSetting("instabilityPostCorrectionEnergy", "0.01")
