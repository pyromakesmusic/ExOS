import xos

def init_main():
    test_config = xos.configLoader("test_config2.txt")
    """
    Currently, the configuration file contains:
        Filepaths to:
        - the robot (ROB/URDF, this one is a ROB)
        - the muscle attachment file (CSV)
        - the world file (XML)
        As well as configuration constants:
        - the control rate
        - the IP address sending the control inputs (string datatype)
        - the network socket to receive inputs on (integer datatype)
    """
    exo_test = xos.ExoGUI(test_config)

if __name__ == "__main__":
    init_main()