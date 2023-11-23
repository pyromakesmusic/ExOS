"""
LIBRARY IMPORTS
"""
# Standard Libraries
import tkinter as tk
from datetime import datetime
import asyncio
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
import pyttsx3  # Text to speech
import vosk  # Voice recognition library
import cv2  # Take camera input

# My Custom Libraries
from . import system_strings as sysvx
from ..apps.apps import Map, Camera, Compass, Clock, DateWidget, MissionWidget

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

class VoiceAssistantUI: # For voice control
    # Should be most of the audio interaction with a UI
    def __init__(self, voice_index: int, rate: int):
        # TTS Engine Initialization
        self.voice_engine = pyttsx3.init()
        self.voices = self.voice_engine.getProperty("voices")
        self.voice_engine.setProperty('rate', rate)
        self.voice_engine.setProperty('voice', self.voices[voice_index].id)

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
        # Plays all the strings and voices in the catalog to test for audio quality.
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


class AugmentOverlayUI:
    # For a Heads-Up Display or Helmet Mounted Display
    def __init__(self, controller, assistant, has_missions=True, has_map=True,
                 has_camera=True, has_clock=True, has_date=True, has_compass=False):
        # boolean values are rapidly becoming more of them
        self.root_HUD = ctk.CTk()  # root_HUD is the tkinter root window

        if not assistant:
            # If no voice assistant assigned uses the controller's built-in assistant
            self.assistant = controller.assistant
        else:
            # Applies the assigned voice assistant
            self.assistant = assistant

        # HUDisplay options using tkinter

        self.root_HUD.overrideredirect(True)  # Makes it borderless
        self.root_HUD.geometry("1920x1080+0+0")  # Sets the size of the window
        self.root_HUD.attributes("-alpha", 0.5)  # Make the window transparent
        self.root_HUD.configure(background="black")  # Makes the background black

        # Sets up the map
        if has_map:
            self.map = Map(self.root_HUD, w=300, h=250)
            self.map.widget.grid(row=3,column=5)
        else:
            self.map = None

        # Sets up the clock
        if has_clock:
            self.clock = Clock(self.root_HUD)
            self.clock.grid(row=3,column=0, sticky="sw")
        else:
            self.clock = None

        # Sets up the date widget
        if has_date:
            self.date = DateWidget(self.root_HUD)
            self.date.grid(row=0,column=0, sticky="nw")
        else:
            self.date = None

        # Sets up compass
        if has_compass:
            self.compass = Compass(self.root_HUD)
            self.compass.grid(column=2,row=2, sticky="n")
        else:
            self.compass = None

        # Sets up the camera feed and display if present
        if has_camera:
            self.camera = Camera(0)
        else:
            self.camera = None

        # Sets up mission info display
        if has_missions:
            self.missions = MissionWidget(self.root_HUD, "no missions")
            self.missions.grid(column=5,row=0, sticky="ne")
        else:
            self.missions = None

        self.stop = ctk.CTkButton(self.root_HUD, command=lambda:asyncio.run(self.close_all()), text="STOP", font=("System", 200),
                                  fg_color="transparent", text_color="red", width=800)
        self.stop.grid(column=1,row=0)

        # Style changes
        self.hud_color = "red"
        self.root_HUD.focus_force()
        self.root_HUD.mainloop()

    async def close_HUD(self):
        # Closes the root_HUD
        self.assistant.announce("Closing heads-up display.")
        self.root_HUD.destroy()
        self.assistant.shutdown_assistant()

    async def close_all(self):
        # Closes the root_HUD
        self.assistant.announce("Shutting down system.")
        self.root_HUD.destroy()
        self.assistant.shutdown_assistant()
        self.controller.shutdown()

    def refresh(self):
        # Update everything on the screen
        self.hud_color = "blue"
        pass

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