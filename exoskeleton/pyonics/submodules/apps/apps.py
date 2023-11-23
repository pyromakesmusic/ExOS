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
        self.widget = tkintermapview.TkinterMapView(root, width=w, height=h)

class Clock(ctk.CTkLabel):
    def __init__(self, root_HUD):
        # Adds a clock
        self.time = datetime.now().strftime("%H:%M:%S")
        self.clock = ctk.CTkLabel.__init__(self, master=root_HUD, text=self.time,
                                           font=("System", 20))  # Actual Tkinter Object
    def update(self):
        self.time = datetime.now().strftime("%H:%M:%S")
        self.clock.configure(text=self.time)
        self.clock.after(1000, self.update)  # Update every 1000 milliseconds (1 second)

class Compass(ctk.CTkLabel):
    def __init__(self, root_HUD):
        # Adds a clock
        self.bearing = "north"
        self.widget = ctk.CTkLabel.__init__(self, master=root_HUD, text=self.bearing,
                                           font=("System", 20))  # Actual Tkinter Object
    def update(self):
        self.bearing = "west"
        self.widget.configure(text=self.bearing)
        self.widget.after(1000, self.update)  # Update every 1000 milliseconds (1 second)
class DateWidget(ctk.CTkLabel):
    def __init__(self, root_HUD):
        # Adds a clock
        self.date = datetime.now().strftime("%H:%M:%S")
        self.widget = ctk.CTkLabel.__init__(self, master=root_HUD, text=self.date,
                                            font=("System", 20))  # Actual Tkinter Object
    def update(self):
        self.date = datetime.now().strftime("%H:%M:%S")
        self.widget.configure(text=self.date)
        self.date.after(60000, self.update)  # Update every 1000 milliseconds (1 second)

class MissionWidget(ctk.CTkLabel):
    def __init__(self, root_HUD, missions):
        # Adds a clock
        self.missions = missions
        self.widget = ctk.CTkLabel.__init__(self, master=root_HUD, text=self.missions,
                                            font=("System", 20))  # Actual Tkinter Object
    def update(self, missions):
        self.missions = missions
        self.widget.configure(text=self.missions)
        self.widget.after(60000, self.update)  # Update every 60000 milliseconds (60 seconds) or 1 minute

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