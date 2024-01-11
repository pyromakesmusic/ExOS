import gpsd  # GPS library
import cv2  # Camera library
from datetime import datetime
import asyncio
# Klamp't imports
import klampt
import klampt.model.coordinates

# Each app should be its own class

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

class Camera(klampt.vis.glcommon.GLProgram):
    def __init__(self, i):
        klampt.vis.glcommon.GLProgram.__init__(self)
        # Launches with an index of a particular camera
        self.camera = None
        self.state = "minimized"  # Can also be "fullscreen", "windowed", "closed"

        self.ret = None
        self.frame = None
        self.shutdown_flag = False




    def cam_launch(self, index):
        # Start the camera
        try:
            self.camera = cv2.VideoCapture(index)
        except:
            "Error: Exception launching camera input."

        while not self.shutdown_flag:
            asyncio.run(self.cam_loop())

    def cam_loop_synchronous(self):
        self.ret, self.frame = self.camera.read()

        # Check if the frame was read successfully
        if not self.ret:
            print("Error: Could not read frame.")

        # Display the frame
        cv2.imshow('Webcam', self.frame)
        return self.frame

    async def cam_loop(self):
        self.ret, self.frame = self.camera.read()

        # Check if the frame was read successfully
        if not self.ret:
            print("Error: Could not read frame.")


        # Display the frame
        cv2.imshow('Webcam', self.frame)
        return self.frame

    def cam_shutdown(self):
        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.shutdown_flag = True

# Desktop Applications

"""
Simulation
"""
class Sim(klampt.sim.simulation.SimpleSimulator):
    """
    This is a class for Simulations. It will contain the substepping logic where forces are applied to simulated objects.
    """
    def __init__(self, wm, robot, timestep):
        klampt.sim.simulation.SimpleSimulator.__init__(self, wm)
        self.dt = timestep
        self.world = wm
        self.robotmodel = robot
        self.link_transforms_start = [self.robotmodel.link(x).getTransform() for x in range(self.robotmodel.numLinks())]
        self.link_transforms_end = None
        self.link_transforms_diff = None


    def simLoop(self, force_list):
        """
        robot: A RobotModel.
        force_list: Not sure what data structure, maybe a dataframe? name of muscle as index, with force and transform

        Should possibly return a list of new transforms to be used for calculating stuff in the next time step.

        """
        wm = self.world

        self.link_transforms_start = [self.robotmodel.link(x).getTransform() for x in range(self.robotmodel.numLinks())]
        """
        Now here adding a section to make sure the muscles contract in the simulation.
        """
        for force in force_list:
            link = self.body(self.robotmodel.link(force[0]))  # From the force info, gets the link to apply force
            force_vector = force[1]  # Gets the force vector
            transform = force[2]  # Gets the transform at which to apply force
            link.applyForceAtLocalPoint(force_vector, transform)

        self.simulate(self.dt)
        self.updateWorld()
        """
        Maybe here is where we have to get the updated link transforms and return them as "sensor" feedback.
        """
        self.link_transforms_end = [self.robotmodel.link(x).getTransform() for x in range(self.robotmodel.numLinks())]

        self.link_transforms_diff = [klampt.math.se3.error(self.link_transforms_start[x], self.link_transforms_end[x])
                                for x in range(len(self.link_transforms_start))]  # Takes the Lie derivative from start -> end
        return self.link_transforms_end  # I don't even know if we need to use this, depends on if we pass by ref or var
