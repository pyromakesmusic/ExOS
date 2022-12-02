"""
LIBRARY IMPORTS
"""
import sys
sys.path.append(r"C:\Users\Pyro\Documents\Math4157\Pyonics\pyonics")

from control import pid
from interface import interface
from pyonics.simulation import physics, simulation
import tkinter as tk


"""
CLASS DEFINITIONS
"""

"""
FUNCTION DEFINITIONS
"""


def main():
    interface.initialize()
    return

if __name__ == "__main__":
    main()