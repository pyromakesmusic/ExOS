import numpy as np
import pandas as pd
import tkinter as tk
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import differint

class Sim():
    def __init__(self):
        x = np.linspace(0,100, num=10)
        y = np.linspace(0,100, num=10)
        self.root = tk.Tk()
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.draw()
        plt.plot(x,y)

        derivative = np.gradient(y)
        der_series = pd.Series(derivative)
        print(derivative)
        differint.RL()
        print(der_series)
        print(len(der_series))
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)
        plt.show()
        return

def main():
    window = Sim()
    return

main()