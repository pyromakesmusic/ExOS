import xos

test_config = xos.configLoader("demo_config.txt")
"""
Currently, the configuration file contains filepaths to:
- the robot (ROB/URDF, this one is a ROB)
- the muscle attachment file (CSV)
- the world file (XML)
"""
exo_test = xos.ExoGUI(test_config)