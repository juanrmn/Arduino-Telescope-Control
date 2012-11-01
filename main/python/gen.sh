#!/bin/bash 

# Generate UI
pyuic4 ./ui/laser_control.ui -o ./ui/laser_control_ui.py 
pyrcc4 ./ui/icons_set.qrc -o ./ui/icons_set_rc.py 

