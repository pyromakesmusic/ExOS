import gpsd  # GPS library
import cv2  # Camera library
from datetime import datetime
import customtkinter as ctk
import tkintermapview

# Might it not make more sense to make each App its own Class?
"""
Functions
"""
def get_gps_data():
    # Connect to the local gpsd service (default host and port)
    gpsd.connect()

    # Get the GPS data
    packet = gpsd.get_current()

    # Check if the data is valid
    if packet.mode >= 2:
        latitude = packet.lat
        longitude = packet.lon
        altitude = packet.alt

        return(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}")
    else:
        return("No GPS fix")

"""
Classes
"""
class Map:
    def __init__(self, root, w, h):
        self.display = tkintermapview.TkinterMapView(root, width=w, height=h)
        self.latitude = None
        self.longitude = None
        self.altitude = None

        self.bearing = "east"
        self.widget = None
    def get_gps_data(self):
        # Connect to the local gpsd service (default host and port)
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
    def __init__(self):
        # Adds a clock
        self.time = datetime.now().strftime("%H:%M:%S")
        self.display = None
    def update(self):
        self.time = datetime.now().strftime("%H:%M:%S")
        return self.time

class Compass:
    def __init__(self):
        self.bearing = "east"
        self.display = None
        self.widget = None
        # Adds a clock
    def update(self):
        self.bearing = "west"

    def set_widget(self, widget):
        self.widget = widget

class DateWidget:
    def __init__(self):
        # Adds a clock
        self.date = datetime.now().strftime("%H:%M:%S")
        self.display = None
    def update(self):
        self.date = datetime.now().strftime("%H:%M:%S")
        return self.date

class MissionWidget:
    def __init__(self):
        # Adds a clock
        self.missions = "Mission text"
    def update(self, missions):
        self.missions = missions
        return self.missions

class Camera:
    def __init__(self, i):
        # Launches with an index of a particular camera
        self.camera = None
        self.cam_launch(i)

        self.ret = None
        self.frame = None


    def cam_launch(self, index):
        # Start the camera
        try:
            self.camera = cv2.VideoCapture(index)
        except:
            "Error: Exception launching camera input."

    def cam_loop(self):
        self.ret, self.frame = self.camera.read()

        # Check if the frame was read successfully
        if not self.ret:
            print("Error: Could not read frame.")

        # Display the frame
        cv2.imshow('Webcam', self.frame)

    def cam_shutdown(self):
        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass