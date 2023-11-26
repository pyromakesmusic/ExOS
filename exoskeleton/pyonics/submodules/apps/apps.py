import gpsd  # GPS library
import cv2  # Camera library
from datetime import datetime
import asyncio
# Klamp't imports
import klampt
import klampt.model.coordinates

# Might it not make more sense to make each App its own Class?

"""
Classes
"""
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
        self.cam_launch(i)
        self.state = "minimized"  # Can also be "fullscreen", "windowed", "closed"

        self.ret = None
        self.frame = None


    def cam_launch(self, index):
        # Start the camera
        try:
            self.camera = cv2.VideoCapture(index)
        except:
            "Error: Exception launching camera input."

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
        return self.frame

        # Display the frame
        #cv2.imshow('Webcam', self.frame)
    def cam_shutdown(self):
        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass