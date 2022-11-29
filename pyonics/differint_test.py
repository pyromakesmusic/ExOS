import numpy as np
import pandas as pd
from differint import differint
import tkinter as tk
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Sim():
    def __init__(self):
        x = np.linspace(0,100, num=10)
        y = np.linspace(0,100, num=10)
        self.root = tk.Tk()
        self.fig, self.ax = plt.subplots(111)
        plt.plot(x,y)

        derivative = np.gradient(y)
        der_series = pd.Series(derivative)
        dfint = differint.RL(4,x)
        print(derivative)
        print(der_series)
        print(len(der_series))
        plt.xticks(0,100, num=5)
        plt.yticks(np.linspace(0,100, num=10))
        plt.plot(x,der_series)
        plt.show()
        return

def main():
    window = Sim()
    return

main()