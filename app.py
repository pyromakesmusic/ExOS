import pandas as pd
from matplotlib import pyplot as plt


from control_flow import control
# from config import Config

# pandas options
pd.options.display.width = 0
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# pyplot options
plt.ion()

def main():
    control.initialize()
    return

main()