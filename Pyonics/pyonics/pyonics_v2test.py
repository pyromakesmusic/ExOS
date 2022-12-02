"""
LIBRARY IMPORTS
"""
import sys
sys.path.append("pyonics_path")

from control import pid
from interface import interface
from simulation import physics, simulation
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