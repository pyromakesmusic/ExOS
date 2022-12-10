# For building powered human augmentations.

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 21:55:28 2022
===============
Document Comments:
    10.11.22
    2218h
    I think the index should be separate from the time values. Physics should
    be based on time independent of the index so that I can have a consistent
    indexing scheme regardless of the time resolution of the data.

    11.3.22
    0944h
    Interface is mostly done. Needs the graph to actually be updating inside
    the GUI but otherwise the front end is ready for a presentation. Adding
    the fractional calculus functionality will be next.

    12.2.22
    2021h
    Trying to refactor into smaller pieces.
===============
LIBRARY IMPORTS
===============
"""

# Local Submodules

import pyonics.submodules.interface.interface as interface

# External Libraries

import pandas as pd
import matplotlib.pyplot as plt

"""
CONFIG
"""
# pandas options
pd.options.display.width = 0
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# pyplot options
plt.ion()


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