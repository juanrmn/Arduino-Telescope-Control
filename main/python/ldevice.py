#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import math
import serial, os
from serial.tools import list_ports
import logging
from PyQt4 import QtCore
import asyncore, socket
from time import sleep, time, strftime, localtime
from string import replace
import coords

# Check for pyserial version ( >= 2.6 nedded)
if serial.VERSION < '2.6':
    print("pySerial >= 2.6. is needed (in Linux you can install 'pip' and then run 'pip install pyserial --upgrade' as root)")
    sys.exit()

## \brief Class that implements the interface to control the device.
# 
# It is designed to work on a separate thread. The communication with the main application is via 
# asynchronous Qt signals.
# Also it uses some functions present in coords.py
#
class LaserDev (QtCore.QThread):
    ## @var init_received
    #  Signal for the communications with the main thread
    #  It emmits when the device is successfully initialized
    init_received = QtCore.pyqtSignal() #X, Y
    
    ## @var pos_received
    #  Signal for the communications with the main thread
    #  It emits when the horizontal coordinates are received from the device
    pos_received = QtCore.pyqtSignal(str, str) #alt, az
    
    ## @var pos_e_received
    #  Signal for the communications with the main thread
    #  It emits when the equatorial coordinates are received from the device
    pos_e_received = QtCore.pyqtSignal(str, str) #ar, dec


    ## Class constructor
    #
    #  Sets the device connection by the serial port
    #
    # \param usb_serial Serial port. By default is '/dev/ttyUSB0'
    # \param usb_serial_port Transmission speed. Default 9600 baud
    # \param timeout Maximum waiting time for responses
    def __init__(self, usb_serial='/dev/ttyUSB0', usb_serial_baud=9600, timeout=2):
        QtCore.QThread.__init__(self, None)
        self.serial = serial.Serial(usb_serial, usb_serial_baud, timeout=timeout)
        logging.debug("Connected (%s)" % usb_serial)
        
    ## Getting the response of sent commands
    #
    #  Implements the common process for getting response of a command
    #
    # \param expect Regular expression for the "end of the command" tag. By default is '^cmd$'
    # \param wait Maximum number of cycles to wait for the response
    # \return Last line read
    def sread(self, expect='^cmd$', wait=0):
        _d = None
        exp = re.compile(expect)
        line = self.serial.readline().rstrip()
        tag_steps = re.compile('^p_.*$')
        tag_horizontal = re.compile('^h_.*$')
        tag_equatorial = re.compile('^e_.*$')
        _count = 0
        while(not exp.match(line) and _count <= wait):
            if tag_steps.match(line):
                resp = line.replace("p_", '')
                _d = resp.split(' ')
                logging.debug("Steps: (%s, %s)" % (_d[0], _d[1]))
            elif tag_horizontal.match(line):
                resp = line.replace("h_", '')
                _d = resp.split(' ')
                self.pos_received.emit(_d[0], _d[1])
                logging.debug("PosH: (%s / %s)" % ( coords.deg_2_degStr( 360.0 - coords.radStr_2_deg(_d[0])), coords.deg_2_degStr( coords.radStr_2_deg(_d[1])) ))
            elif tag_equatorial.match(line):
                resp = line.replace("e_", '')
                _d = resp.split(' ')
                self.pos_e_received.emit(_d[0], _d[1])
                logging.debug("PosE: (%s / %s)" % ( \
                    coords.hour_2_hourStr(coords.rad_2_hour(coords.degStr_2_rad(coords.radStr_2_degStr(_d[0])))), \
                    coords.deg_2_degStr(coords.radStr_2_deg(_d[1])) ))
            if line == '':
                _count += 1
            else:
                print("__debug__: %s" % line)
            line = self.serial.readline().rstrip()
        return line

    ## Sets initial time in the device
    #
    # \param time Unix timestamp
    def setTime(self, time):
        self.serial.write("time")
        if(self.serial.readline().rstrip() == 'float'):
            self.serial.write( coords.rad_2_radStr(coords.hourStr_2_rad(time)) )
            self.sread()
        
    ## Initializes the device
    #
    #  Emits the init_received when the device responds
    def init(self):
        self.serial.readline() # wait the timeout at most
        self.serial.write('init')
        
        self.sread(expect='^done_init$', wait=20)
        self.init_received.emit()
        
    ## Initializes the execution thread
    #
    def run(self):
        self.init()
    
    ## Sets a reference object in the device
    #
    #
    # \param id_rel Number of the reference object, 1, 2 or 3
    # \param ra Right ascension
    # \param dec Declination
    # \param time Timestamp of the measure
    def setRef(self, id_ref, ra, dec, time):
        setf = {1: 'set1', 2: 'set2', 3: 'set3'}
        logging.debug(" %s(%s, %s, %s)" % (setf[id_ref], ra, dec, time))
        self.serial.write(setf[id_ref])
        if(self.serial.readline().rstrip() == 'float'):
            self.serial.write( coords.rad_2_radStr(coords.hourStr_2_rad(ra)) )
            self.serial.write( coords.rad_2_radStr(coords.degStr_2_rad(dec)) )
            self.serial.write( coords.rad_2_radStr(coords.hourStr_2_rad(time)) )
            self.sread(wait=5)
        
    ## Points the device toward the given equatorial coordinates
    #
    # \param ra Right ascension
    # \param dec Declination
    # \param time Timestamp of the measure
    def goto(self, ra, dec, time):
        logging.debug("(%s, %s, %s)" % (ra, dec, time))
        self.serial.write('goto')
        if(self.serial.readline().rstrip() == 'float'):
            self.serial.write( coords.rad_2_radStr(coords.hourStr_2_rad(ra)) )
            self.serial.write( coords.rad_2_radStr(coords.degStr_2_rad(dec)) )
            self.serial.write( coords.rad_2_radStr(coords.hourStr_2_rad(time)) )
            self.sread(wait=10)
        
    ## Points the device toward the given horizontal coordinates
    #
    # \param ac Azimut
    # \param alt Altitude
    def move(self, ac, alt):
        logging.debug("(%s, %s)" % (ac, alt))
        self.serial.write('move')
        if(self.serial.readline().rstrip() == 'float'):
            self.serial.write( coords.rad_2_radStr(6.283185 - coords.degStr_2_rad(ac)) )
            self.serial.write( coords.rad_2_radStr(coords.degStr_2_rad(alt)) )
            self.serial.write( coords.rad_2_radStr(coords.hourStr_2_rad(strftime("%Hh%Mm%Ss", localtime()))) )
            self.sread(wait=10)
            
    ## Starts the accelerated movement along the X axis, in the given direction
    #
    # \param signDir Direction of movement: 1 means clockwise direction, 0 means counter clockwise
    def movx(self, signDir):
        self.serial.write('movx')
        self.serial.write(signDir)
    
    ## Starts the accelerated movement along the Y axis, in the given direction
    #
    # \param signDir Direction of movement. 1 means upwards, 0 means downwards
    def movy(self, signDir):
        self.serial.write('movy')
        self.serial.write(signDir)

    ## Stops the accelerated movement on both axes
    #
    def stop(self):
        self.serial.write('stop')
        resp = self.sread(expect = '^done_.*')
        if resp == 'done_end':# End sensor reached ..
            self.sread()#.. 
            self.sread()#.. so we expect an extra cmd
        else:
            self.sread()
        
    ## Turn the laser On
    #
    def laserOn(self):
        self.serial.write('laon')
        self.sread(wait=3)
    
    ## Turn the laser Off
    #
    def laserOff(self):
        self.serial.write('loff')
        self.sread(wait=3)
    
# Function to scan available serial ports...
#
# \return List of available serial ports
def get_avalilable_ports():
    available = []
    
    ## Windows (I cannot test this part..)
    #if os.name == 'nt':
    #    for i in range(256):
    #        try:
    #            s = serial.Serial(i)
    #            available.append('COM'+str(i + 1))
    #            s.close()
    #        except serial.SerialException:
    #            pass
    ## Mac / Linux
    #else:
    
    # We only want the USB-Serial ports:
    for port in list_ports.comports():
        if port[0].find('USB') != -1:
            available.append(port[0])
    
    return available
