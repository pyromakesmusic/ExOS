import xos

test_config = xos.configLoader() # Config currently contains filepaths of each subRobot, will probably add other stuff
exo_test = xos.ExoGUI(test_config)