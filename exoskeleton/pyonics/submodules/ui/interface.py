"""
LIBRARY IMPORTS
"""
# Standard Libraries
import tkinter as tk
from datetime import datetime

import gpsd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ipywidgets as widgets
from time import strftime
import pyaudio
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Third Party Libraries
import tkintermapview  # Adds potential for maps to tkinter
import pyttsx3  # Text to speech
import vosk  # Voice recognition library
import cv2  # Take camera input

# My Custom Libraries
from . import system_strings as sysvx
"""
FUNCTION DEFINITIONS #1 
"""
# Most of them should go here, any down after the class definitions are there only to avoid screwing things up right now

"""
CLASS DEFINITIONS
"""
# Parent Class

class VoiceAssistant: # For voice control
    def __init__(self):
        # TTS Engine Initialization
        self.voice_engine = pyttsx3.init()
        self.voices = self.voice_engine.getProperty("voices")
        self.voice_engine.setProperty('rate', 150)
        self.voice_engine.setProperty('voice', self.voices[1].id)

        self.recog_model = None
        self.voice_recog = None
        self.user_cam = None

        self.mic = None
        self.stream = None
        self.voice_launch()

        self.voice_test()

    def shutdown_assistant(self):
        pass

    def announce(self, stringvar):
        print(stringvar)
        self.voice_engine.say(stringvar)
        self.voice_engine.runAndWait()
        return

    def voice_launch(self):
        # Voice Recognition Initialization
        self.recog_model = vosk.Model(model_name="vosk-model-small-en-us-0.15")
        self.voice_recog = vosk.KaldiRecognizer(self.recog_model, 16000)
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=81)
        self.stream.start_stream()
        # Tests/ Strings
        self.voice_engine.runAndWait()

    def voice_loop(self):
        data = self.stream.read(1024)
        if self.voice_recog.AcceptWaveform(data):
            text = self.voice_recog.Result()
            print(f"{text[14:-3]}")
            return(text)



    def cam_loop(self):
        ret, frame = self.user_cam.read()

        # Check if the frame was read successfully
        if not ret:
            print("Error: Could not read frame.")

        # Display the frame
        cv2.imshow('Webcam', frame)

        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.shutdown_assistant()

    def camera_launch(self):
        try:
            self.user_cam = cv2.VideoCapture(0)
        except:
            "Error: Exception launching camera input."


    def voice_test(self):
    # Plays all the strings in the catalog to test for audio quality.
        self.announce(sysvx.test_string1)
        self.announce(sysvx.access_denied)
        self.announce(sysvx.ready_string1)
        self.announce(sysvx.lowpower_string1)
        self.announce(sysvx.malfunction_string1)
        self.announce(sysvx.no_auth_string1)

        for voice in self.voices:
            print(voice, voice.id)
            self.voice_engine.setProperty('voice', voice.id)
            self.voice_engine.say("Hello World!")
            self.voice_engine.runAndWait()
            self.voice_engine.stop()


class AugmentOverlay:
    # For a Heads Up Display or Helmet Mounted Display
    def __init__(self, controller, assistant):
        self.HUD = None
        if not assistant:
            # If no assistant assigned uses the controller's built-in assistant
            self.assistant = controller.assistant
        else:
            self.assistant = assistant

        self.clock_text = None

        self.objective_text = None

        self.text_buffer = None

        self.gps_text = None

        self.clock = None

        self.objectives = None

        self.gps = None
        self.map = None

        # Empty variable creation
        self.date_text = None
        self.date = None



        # Style changes
        self.hud_color = "red"


        self.create_HUD()

    def close_HUD(self):
        # Closes the HUD
        self.assistant.announce("Shutting down heads-up display.")
        self.HUD.destroy()
        self.assistant.announce("Shutting down controller.")

    def create_HUD(self):
        # Initializes the HUD

        self.HUD = tk.Tk()  # Creates the HUD visual area as a tKinter window
        self.HUD.overrideredirect(True)  # Makes it borderless
        self.HUD.geometry("1920x1080")  # Sets the size of the window
        self.HUD.attributes("-alpha", 0.5)  # Make the window transparent
        self.HUD.configure(background="black")  # Makes the background black
        self.text_buffer = tk.StringVar()  # Creates a text buffer

        # empty variable creation
        self.objective_text = "Missions:"
        self.objectives = None
        self.clock_text = None
        self.clock = None

        self.gps_text = None
        self.gps = None
        self.latitude = None
        self.longitude = None
        self.altitude = None



        self.configure_HUD()  # sets up the HUD layout by user preference

        self.HUD.mainloop()
        self.HUD.focus_force()

    def update_HUD(self):
        # Update the label's text
        self.update_datetime()
        self.update_GPS()
        pass

    def configure_HUD(self):

        # Create a close button
        self.objectives = tk.Label(self.HUD, text=self.objective_text, font=("System", 20), fg=self.hud_color,
                                   bg="black")
        self.objectives.pack(anchor="ne", padx=5)

        # Adds a clock
        self.clock = tk.Label(self.HUD, text=self.clock_text, font=("System", 20), fg=self.hud_color, bg="black")

        self.date = tk.Label(self.HUD, text=self.date_text, font=("System", 20), fg=self.hud_color, bg="black")

        self.gps = tk.Label(self.HUD, text=self.gps_text, font=("System", 20), fg=self.hud_color, bg="black")

        self.map = tkintermapview.TkinterMapView(self.HUD, width=800, height=600)
        self.map.pack(anchor="se")

        self.date.pack(anchor="nw", padx=5)

        self.clock.pack(anchor="sw", pady=450)

        self.gps.pack(anchor="se", padx=100, pady=300)


        self.update_datetime()
        self.update_GPS()

    def update_GPS(self):
        try:
            gpsd.connect()

            # Get the GPS data
            packet = gpsd.get_current()

            # Check if the data is valid
            if packet.mode >= 2:
                self.latitude = packet.lat
                self.longitude = packet.lon
                self.altitude = packet.alt

                coordinates = (f"Latitude: {self.latitude},\nLongitude: {self.longitude},\nAltitude: {self.altitude}")
            else:
                coordinates = ("No GPS fix")

            self.gps_text = coordinates

        except ConnectionRefusedError:
            self.gps_text = "GPS connection failed..."

        self.gps.config(text=self.gps_text)
        self.gps.after(1000, self.update_GPS)

    def update_datetime(self):
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date.config(text=current_date)
        self.clock.config(text=current_time)
        self.clock.after(1000, self.update_datetime)  # Update every 1000 milliseconds (1 second)
        self.date.after(1000, self.update_datetime)

"""
FUNCTION DEFINITIONS
"""

def initialize():
    pass
"""
Main Function
"""

def main():
    return

if __name__ == "__main__":
    main()