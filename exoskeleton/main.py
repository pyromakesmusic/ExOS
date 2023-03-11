import xos

robot_name = xos.configLoader()
print("Robot name:", robot_name)
exo_test = xos.ExoSimGUI(robot_name)