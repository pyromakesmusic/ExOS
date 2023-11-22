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
import transformers
import customtkinter as ctk
import tkintermapview  # Adds potential for maps to tkinter
import pyttsx3  # Text to speech
import vosk  # Voice recognition library
import cv2  # Take camera input

# My Custom Libraries
from . import system_strings as sysvx
from .. import apps as xapp  # This is where system applications are hosted, they should be low level

"""
FUNCTION DEFINITIONS #1 
"""
# Most of them should go here, any down after the class definitions are there only to avoid screwing things up right now

"""
CLASS DEFINITIONS
"""
# Parent Class

class Personality:
    def __init__(self):
        self.personality_params = {
            'friendliness': 0.5,
            'formality': 0.5,
            'humor': 0.5,
            # Add more personality parameters as needed
            }

    def generate_response(self, user_input, personality_params):
        prompt = f"Personality: {personality_params}\nUser: {user_input}\nAssistant:"
        response = openai.Completion.create( # Change the openai line
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def update_personality(self, personality_params, feedback):
        # Adjust personality parameters based on user feedback
        # Update the values in personality_params
        updated_personality_params = personality_params
        return updated_personality_params

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
        #self.voice_test()

    def shutdown_assistant(self):
        # Shuts down and releases resources
        self.voice_engine.stop()

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

    def voice_test(self):
    # Plays all the strings in the catalog to test for audio quality.
        self.announce(sysvx.test_string1)
        self.announce(sysvx.access_denied)
        self.announce(sysvx.ready_string1)
        self.announce(sysvx.lowpower_string1)
        self.announce(sysvx.malfunction_string1)
        self.announce(sysvx.no_auth_string1)

        test_strings = [sysvx.test_string1, sysvx.access_denied, sysvx.ready_string1, sysvx.lowpower_string1,
                        sysvx.malfunction_string1, sysvx.no_auth_string1]

        i = 0

        for voice in self.voices:
            print(voice, voice.id)
            self.voice_engine.setProperty('voice', voice.id)
            self.voice_engine.say(test_strings[i]) # What they say goes here
            self.voice_engine.runAndWait()
            self.voice_engine.stop()
            i = (i + 1) % len(self.voices)


class AugmentOverlay:
    # For a Heads-Up Display or Helmet Mounted Display
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
        self.latitude = None
        self.longitude = None
        self.altitude = None

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

        self.HUD = ctk.CTk()  # Creates the HUD visual area as a tKinter window
        self.HUD.overrideredirect(True)  # Makes it borderless
        self.HUD.geometry("1920x1080+0+0")  # Sets the size of the window
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

    def refresh_HUD(self):
        # Update the label's text
        self.update_datetime()
        self.update_GPS()
        pass

    def configure_HUD(self):

        # Adds a clock
        self.clock = ctk.CTkLabel(self.HUD, text=self.clock_text, font=("System", 20))
        self.date = ctk.CTkLabel(self.HUD, text=self.date_text, font=("System", 20))
        self.gps = ctk.CTkLabel(self.HUD, text=self.gps_text, font=("System", 20))
        self.map = tkintermapview.TkinterMapView(self.HUD, width=400, height=300)

        # self.map.set_tile_server("http://a.tile.stamen.com/toner/{z}/{x}/{y}.png")  # black and white

        self.map.pack(anchor="ne")
        self.date.pack(anchor="nw")
        self.clock.pack(anchor="sw")

        # This needs to update once early to make sure every box has information, then once every time step
        self.update_datetime()
        self.update_GPS()

    """
    Layout Management
    """

    def create_objectives(self):
        # Sets up objective list on the HUD
        self.objectives = ctk.CTkLabel(self.HUD, text=self.objective_text, font=("System", 20))
        self.objectives.pack(anchor="ne")

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

        self.gps.configure(text=self.gps_text)
        self.gps.after(1000, self.update_GPS)

    def update_datetime(self):
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date.configure(text=current_date)
        self.clock.configure(text=current_time)
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