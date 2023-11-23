import gpsd  # GPS library
import cv2  # Camera library
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
    def __init__(self):
        self.map = tkintermapview.TkinterMapView(self.HUD, width=1000, height=1000)

class Camera:
    def __init__(self, i):
        # Launches with an index of a particular camera
        self.camera = None
        self.cam_launch(i)


    def cam_launch(self, index):
        # Start the camera
        try:
            self.camera = cv2.VideoCapture(0)
        except:
            "Error: Exception launching camera input."

    def cam_loop(self):
        ret, frame = self.camera.read()

        # Check if the frame was read successfully
        if not ret:
            print("Error: Could not read frame.")

        # Display the frame
        cv2.imshow('Webcam', frame)

    def cam_shutdown(self):
        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass