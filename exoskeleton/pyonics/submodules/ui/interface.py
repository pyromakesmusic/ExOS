"""
LIBRARY IMPORTS
"""
# Standard Libraries
import tkinter as tk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ipywidgets as widgets
from time import strftime
import pyaudio
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Third Party Libraries
import pyttsx3
import vosk

# My Custom Libraries

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
        self.mic = None
        self.stream = None
        self.voice_launch()


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

class AugmentOverlay:
    def __init__(self, controller, assistant):
        self.HUD = None
        if not assistant:
            # If no assistant assigned uses the controller's built-in assistant
            self.assistant = controller.assistant
        else:
            self.assistant = assistant
        self.clock_text = None
        self.text_overlay = None
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

        # Empty variable creation
        self.date_text = None
        self.date = None


        self.configure_HUD()  # sets up the HUD layout by user preference

        self.HUD.mainloop()
        self.HUD.focus_force()

    def update_HUD(self):
        # Update the label's text
        pass

    def configure_HUD(self):

        # Create a close button
        self.objectives = tk.Label(self.HUD, text=self.objective_text, font=("System", 20), fg=self.hud_color,
                                   bg="black")
        self.objectives.pack(anchor="ne", padx=5)

        # Adds a clock
        self.clock = tk.Label(self.HUD, text=self.clock_text, font=("System", 20), fg=self.hud_color, bg="black")

        self.date = tk.Label(self.HUD, text=self.date_text, font=("System", 20), fg=self.hud_color, bg="black")

        self.date.pack(anchor="nw", padx=5)

        self.clock.pack(anchor="sw", pady=450)


        self.update_datetime()

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