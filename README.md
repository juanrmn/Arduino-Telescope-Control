Telescope control with Stellarium and Arduino
==============================================


This project consists on a first approach to control a telescope mechanism, builded from scratch and
based on Arduino microcontroller, from a computer **with GNU/Linux** and the Stellarium software.

By the moment, the code has been tested only in a mini-dobsonian mount with a green laser pointer instead 
of a real telescope. The laser points towards the celestial objects indicated from Stellarium, by using a
stepper motors system.

![Device](https://raw.github.com/juanrmn/Arduino-Telescope-Control/master/images/photo_1_small.jpg)

You can see more images, schematics and parts details in the images folder.


Software
---------

The software is divided on two main blocks, the first one implemented in Python (computer) and the other
one for Arduino microcontroller (device):

In the computer side with Python:

* Communications with Stellarium ([Stellarium Telescope Protocol](http://www.stellarium.org/wiki/index.php/Telescope_Control_(client-server\)), [python-bitstring](http://code.google.com/p/python-bitstring/)))
* Communications with the device (USB-Serial)
* User interface (PyQt4)

Device with Arduino:

* Communications with the computer (receiving commands and parameters, and sending responses)
* Coordinate transformations (based on Toshimi Taki's [Matrix Method for Coodinates Transformation](http://www.geocities.jp/toshimi_taki/matrix/matrix.htm))
* Control mechanisms (stepper motors, sensors, positioning..)



### testing folder

Contains the necessary scripts for testing isolately the communications with Stellarium, communications with the device, 
and the Arduino library for coordinate transformation (Matrix Method implementation).


### main folder

Software to control the "Laser pointer device" with Stellarium, including GUI.


### docs folder

Datasheets and Matrix method documentation.


### bitstring-3.0.2 folder

A Python module that makes the creation, manipulation and analysis of binary data as simple and natural as possible.

Bitstring project page: http://code.google.com/p/python-bitstring/


More Info
---------

http://yoestuve.es/blog/telescope-control-with-stellarium-and-arduino/

http://yoestuve.es/blog/category/laser-pointer/
