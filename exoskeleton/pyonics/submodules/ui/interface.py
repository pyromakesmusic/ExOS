"""
LIBRARY IMPORTS
"""
# Standard Libraries
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import ipywidgets as widgets
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
        self.text_buffer = None
        self.text_overlay = None
        self.create_HUD()

    def HUD_close(self):
        self.assistant.announce("Shutting down heads-up display.")
        self.HUD.destroy()
        self.assistant.announce("Shutting down controller.")

    def create_HUD(self):
        # Creates the HUD visual area as a tKinter window
        self.HUD = tk.Tk()
        self.HUD.overrideredirect(True)
        self.HUD.geometry("1920x1080")
        # Make the window transparent
        self.HUD.attributes("-alpha", 0.2)
        self.text_buffer = tk.StringVar()
        self.text_overlay = tk.Label(self.HUD, textvariable="placeholder", font=("System", 100))
        self.text_overlay.pack()
        # Create a close button
        close_button = tk.Button(self.HUD, text="PLACEHOLDER", command=self.HUD_close)
        close_button.pack(pady=10)
        self.HUD.mainloop()

    def update_HUD(self):
        # Update the label's text
        current_text = self.controller.input
        print(current_text)
        self.text_buffer.set(current_text)
        self.text_overlay = tk.Label(self.HUD, textvariable=self.text_buffer, font=("System", 100))
        self.text_overlay.pack()


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