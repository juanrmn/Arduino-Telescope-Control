#!/usr/bin/python -d
# -*- coding: utf-8 -*-
 
import sys
import signal, os
import functools
import logging
from PyQt4 import QtCore, QtGui
from threading import Thread, Event
from time import ctime, strftime, localtime
from ui.laser_control_ui import Ui_LaserControl
from telescope_server import Telescope_Server
import coords
from ldevice import LaserDev, get_avalilable_ports
from repeat_timer import RepeatTimer


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

try:
    _toUtf8 = QtCore.QString.toUtf8
except AttributeError:
    _toUtf8 = lambda s: s

logging.basicConfig(level=logging.DEBUG, format="%(filename)s: %(funcName)s - %(levelname)s: %(message)s")


## \brief Main class that coordinates all the necessary elements and the user interface
# 
# Uses the Telescope_Server and LaserDev modules in order to coordinate the communications between the
# elements and the user interface with PyQt4
#
class LaserControlMain(QtGui.QMainWindow):
    ## @var act_stell_pos
    #  Signal to communications with the Telescope_Server instance
    #  It emits when we want to send to Stellarium the equatorial coordinates
    act_stell_pos = QtCore.pyqtSignal(str, str)

    ## Class constructor
    #
    #  Starts the UI and the Telescope_Server instance
    #
    #  \param parent (optional) Parent object. By default is None
    def __init__(self, parent=None):
        super(LaserControlMain, self).__init__(parent)
        self.confMode = False
        self.nRef = 0
        self.device = None
        (self._ra, self._dec) = ("0h0m0s", "0º0'0''")

        self.ui = Ui_LaserControl()
        self.ui.setupUi(self)
        self.ui.Reconfigure.setVisible(False)

        regex=QtCore.QRegExp("%s" % (_fromUtf8("^-?[0-9]{1,3}(º|ᵒ)[0-9]{1,3}'[0-9]{1,3}([']{2}|\")$")))
        self.Valid=QtGui.QRegExpValidator(regex, self)
        self.ui.posHorizontal.setValidator(self.Valid)
        self.ui.posVertical.setValidator(self.Valid)
        self.ui.posHorizontal.setText("%s" % (_fromUtf8("0º0'0''")))
        self.ui.posVertical.setText("%s" % (_fromUtf8("0º0'0''")))
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.tabWidget.setTabEnabled(1, False)

        self.pos = ('0.0000', '0.0000')
        self._prev_pos = ("0º0'0''", "0º0'0''")
        
        #Starts server
        self.Server = Telescope_Server(pos_signal=self.act_stell_pos)
        self.Server.daemon = True
        self.Server.start()
        
        self.setSignals()
        self.setShortcuts()
        
        #At the beginning, configuration mode is On
        self.ui.confMode.setChecked(True)
        
    ## Connects the UI signals
    #
    def setSignals(self):
        #Movements
        QtCore.QObject.connect(self.ui.upButton, QtCore.SIGNAL("pressed()"), self.upPressed)
        QtCore.QObject.connect(self.ui.downButton, QtCore.SIGNAL("pressed()"), self.downPressed)
        QtCore.QObject.connect(self.ui.rightButton, QtCore.SIGNAL("pressed()"), self.rightPressed)
        QtCore.QObject.connect(self.ui.leftButton, QtCore.SIGNAL("pressed()"), self.leftPressed)
        QtCore.QObject.connect(self.ui.upButton, QtCore.SIGNAL("released()"), self.arrow_released)
        QtCore.QObject.connect(self.ui.downButton, QtCore.SIGNAL("released()"), self.arrow_released)
        QtCore.QObject.connect(self.ui.rightButton, QtCore.SIGNAL("released()"), self.arrow_released)
        QtCore.QObject.connect(self.ui.leftButton, QtCore.SIGNAL("released()"), self.arrow_released)
        
        #Position
        QtCore.QObject.connect(self.ui.posVertical, QtCore.SIGNAL("editingFinished()"), self.posChanged)
        QtCore.QObject.connect(self.ui.posHorizontal, QtCore.SIGNAL("editingFinished()"), self.posChanged)
        
        #Laser
        QtCore.QObject.connect(self.ui.laserOn, QtCore.SIGNAL("toggled(bool)"), self.laserToggled)
        
        #Options
        QtCore.QObject.connect(self.ui.confMode, QtCore.SIGNAL("toggled(bool)"), self.confModeChanged)
        QtCore.QObject.connect(self.ui.trackMode, QtCore.SIGNAL("toggled(bool)"), self.trackModeChanged)
        
        #Device connection
        self.refreshSerialPorts()
        QtCore.QObject.connect(self.ui.action_Refresh, QtCore.SIGNAL("triggered(bool)"), self.refreshSerialPorts)
        QtCore.QObject.connect(self.ui.action_Desconectar, QtCore.SIGNAL("triggered(bool)"), self.closeDevice)
        #El dispositivo debe recalcular el número de pasos por vuelta en cada eje
        QtCore.QObject.connect(self.ui.action_Recalibrar, QtCore.SIGNAL("triggered(bool)"), self.initDevice)
        
        #Stellarium..
        self.Server.stell_pos_recv.connect(self.stellariumRecv)
    
    ## Show available serial ports and set connection signals
    #
    def refreshSerialPorts(self):
        # Clear menu..
        self.ui.menu_Connect.clear()
        self.ui.menu_Connect.addAction(self.ui.action_Refresh)
        self.ui.menu_Connect.addSeparator()
        
        port_list = get_avalilable_ports()
        for device_path in port_list:
            act = QtGui.QAction(device_path, self)
            act.triggered.connect(functools.partial(self.connectDevice, device_path))
            self.ui.menu_Connect.addAction(act)
        
    ## Shortcuts for the device movements
    #
    def setShortcuts(self):
        self.ui.leftB_shortCut = QtGui.QShortcut(QtGui.QKeySequence("Shift+Left"), self, self.ui.leftButton.animateClick)
        self.ui.rightB_shortCut = QtGui.QShortcut(QtGui.QKeySequence("Shift+Right"), self, self.ui.rightButton.animateClick)
        self.ui.upB_shortCut = QtGui.QShortcut(QtGui.QKeySequence("Shift+Up"), self, self.ui.upButton.animateClick)
        self.ui.downB_shortCut = QtGui.QShortcut(QtGui.QKeySequence("Shift+Down"), self, self.ui.downButton.animateClick)
        
    ## Handles the coordinate reception from Stellarium
    #
    #  Receives the coordinates from Stellarium by the Telescope_Server instance.
    #  If the device is connected, sends the coordinates to it, as either the configuration or movement values.
    #  
    #  Also manages the UI status along the configuration process.
    #
    # \param ra Right ascension
    # \param dec Declination
    # \param mtime Timestamp
    def stellariumRecv(self, ra, dec, mtime):
        ra = float(ra)
        dec = float(dec)
        mtime = float(mtime)
        logging.debug("%s" % coords.toJ2000(ra, dec, mtime))
        (sra, sdec, stime) = coords.eCoords2str(ra, dec, mtime)
        (self._ra, self._dec) = (sra, sdec)

        if self.device != None:
            logging.debug("Sending to the device: '%s','%s','%s'" % (sra, sdec, stime))
            try:
                if self.ui.Reconfigure.isChecked():
                    if self.ui.redef_1:
                        self.ui.redef_1.setChecked(False)
                        redef = 1
                    elif self.ui.redef_2:
                        self.ui.redef_2.setChecked(False)
                        redef = 2
                    else:
                        self.ui.redef_3.setChecked(False)
                        redef = 3
                    self.ui.Reconfigure.setChecked(False)
                    self.device.setRef(redef, sra, sdec, stime)
                elif not self.confMode:
                    self.device.goto(sra, sdec, stime)
                else:
                    self.nRef = self.nRef + 1
                    self.ui.text_status.setText("References: %d/2" % self.nRef)
                    self.device.setRef(self.nRef, sra, sdec, stime)
                    if self.nRef == 2:
                        self.setConfigDone()
                        self.nRef = 0
            except:
                logging.debug("Device not found..")
                e = sys.exc_info()[1]
                print("Error: %s" % e)
    
    ## Up key pushed
    #
    #  Starts the upward movement of the device
    def upPressed(self):
        if self.device != None:
            self.device.movy('1')
    
    ## Down key pushed
    #
    #  Starts the downward movement
    def downPressed(self):
        if self.device != None:
            self.device.movy('0')
    
    ## Right key pushed
    #
    #  Starts the clockwise movement
    def rightPressed(self):
        if self.device != None:
            self.device.movx('1')
    
    ## Left key pushed
    #
    #  Starts the counter clockwise movement
    def leftPressed(self):
        if self.device != None:
            self.device.movx('0')
    
    ## Up/Down/Right/Left key released..
    #
    #  Stops any movement
    def arrow_released(self):
        if self.device != None:
            self.device.stop()
    
    ## Handles the changes on the coordinates text boxes
    #
    #  If the device is configured, sends the new coordinates to it
    def posChanged(self):
        logging.debug("(%s, %s)" % (self.ui.posHorizontal.text(), self.ui.posVertical.text()))
        x = _toUtf8(self.ui.posHorizontal.text())
        y = _toUtf8(self.ui.posVertical.text())
        if self.device != None and (self._prev_pos[0]!=x or self._prev_pos[1]!=y):
            logging.debug("Sending (%s, %s) to device" % (x, y))
            self.device.move(x,y)
        self._prev_pos = (x, y)
        
    ## Handles the changes on "configuration mode" check box
    #
    def confModeChanged(self):
        if self.ui.confMode.isChecked():
            self.confMode = True
            self.nRef = 0
            logging.debug("Conf mode ON")
        else:
            self.setConfigDone()
            self.confMode = False
            logging.debug("Conf mode Off")
    
    ## Handles the end of the device configuration process
    #
    def setConfigDone(self):
        self.ui.confMode.setChecked(False)
        self.ui.tabWidget.setTabEnabled(1, True)
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.text_status.setText("References: 2/2")
        
        self.ui.confMode.setVisible(False)
        self.ui.textEdit.setVisible(False)
        
        self.ui.Reconfigure.setVisible(True)
        
            
    ## Handles changes on tracking check box
    # 
    #  If check is On, starts the tracking mode on the device
    def trackModeChanged(self):
        if self.ui.trackMode.isChecked():
            self.track = RepeatTimer(5.0, self.tracking)
            self.track.start()
            logging.debug("Track mode ON")
        else:
            self.track.cancel()
            logging.debug("Track mode Off")
        
    ## Starts the device connection
    #
    #  In case of error, shows the message on UI
    # \param device_path USB Serial Device path
    def connectDevice(self, device_path):
        self.ui.action_Desconectar.setEnabled(True)
        self.ui.action_Recalibrar.setEnabled(True)
        logging.info("Connecting to device via '%s'" % device_path)
        try:
            if self.device == None:
                self.device = LaserDev(usb_serial=device_path)
                self.device.init_received.connect(self.init_received)
                self.device.pos_received.connect(self.pos_received)
                self.device.pos_e_received.connect(self.pos_e_received)
                self.device.start()
        except:
            logging.info("Device not found")
            QtGui.QMessageBox.warning(self, 'Warning', "Device not found")
            self.ui.action_Desconectar.setEnabled(False)
            self.ui.action_Recalibrar.setEnabled(False)
            self.device = None
            
    ## Initialize device
    #
    #  The device will calculate the steps per revolution
    def initDevice(self):
        logging.info("Initializing device..")
        try:
            if self.device != None:
                self.device.init()
        except:
            logging.info("Error initializing device.")
    
    ## Receives the end of initialization signal from the device
    #
    #  That signal indicates that the device is successfully initialized
    def init_received(self):
        logging.debug("Init received")
        self.pos = ('0.0000', '0.0000')
        self.ui.posHorizontal.setText("%s" % _fromUtf8("0º0'0''"))
        self.ui.posVertical.setText("%s" % _fromUtf8("0º0'0''"))
        
    ## Receives the position updated signal from the device
    #
    #  The parameters are the horizontal coordinates which the device points to
    def pos_received(self, x, y):
        logging.debug("%s,%s" % (x, y))
        self.pos = (x, y)
        self.ui.posHorizontal.setText("%s" % _fromUtf8(coords.deg_2_degStr(360.0 - coords.radStr_2_deg(self.pos[0]))))
        self.ui.posVertical.setText("%s" % _fromUtf8(coords.radStr_2_degStr(self.pos[1])))
        
    ## Receives the position updated signal from the device
    #
    #  The parameters are the equatorial coordinates which the device points to
    def pos_e_received(self, x, y):
        logging.debug("%s,%s" % (x, y))
        self.act_stell_pos.emit(x, y)
                
    ## Tracking mode
    #
    #  Updates periodically the device position by sending the equatorial coordinates and time
    def tracking(self):
        logging.debug("('%s', '%s', '%s')" % (self._ra, self._dec, strftime("%Hh%Mm%Ss", localtime())))
        if self.device != None and self._ra != '0h0m0s':
            self.device.goto( self._ra, self._dec, strftime("%Hh%Mm%Ss", localtime()) )
    
    ## Laser toggle..
    #
    def laserToggled(self):
        if self.ui.laserOn.isChecked():
            if self.device != None:
                self.device.laserOn()
            logging.debug("Laser ON")
        else:
            if self.device != None:
                self.device.laserOff()
            logging.debug("Laser Off")
        
    ## Close the device connection
    #
    def closeDevice(self):
        self.ui.action_Conectar.setEnabled(True)
        self.ui.action_Desconectar.setEnabled(False)
        self.ui.action_Recalibrar.setEnabled(False)
        logging.info("Disconnecting device..")
        try:
            if self.device != None:
                self.device.close()
                self.device = None
        except:
            self.device = None

    ## Exit..
    #
    def closeEvent(self, event):
        logging.debug("Bye!")
        try:
            self.Server.close_socket()
            self.track.cancel()
            event.accept()
        except:
            event.accept()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app_gui = LaserControlMain()
    app_gui.show()
    sys.exit(app.exec_())

