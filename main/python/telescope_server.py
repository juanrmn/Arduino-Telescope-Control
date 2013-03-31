#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from PyQt4 import QtCore
from threading import Thread
import asyncore, socket
from time import time, localtime
from bitstring import BitArray, BitStream, ConstBitStream # http://code.google.com/p/python-bitstring/
import coords


logging.basicConfig(level=logging.DEBUG, format="%(filename)s: %(funcName)s - %(levelname)s: %(message)s")


## \brief Implementation of the server side connection for 'Stellarium Telescope Protocol'
#
#  Manages the execution thread to the server side connection with Stellarium
class Telescope_Channel(QtCore.QThread, asyncore.dispatcher):
    ## @var stell_pos_recv
    # It emits when equatorial coordinates are received from client (Stellarium)
    stell_pos_recv = QtCore.pyqtSignal(str, str, str) #Ra, Dec, Time
    
    ## Class constructor
    #
    # \param conn_sock Connection socket
    def __init__(self, conn_sock):
        self.is_writable = False
        self.buffer = ''
        asyncore.dispatcher.__init__(self, conn_sock)
        QtCore.QThread.__init__(self, None)
        
    ## Indicates the socket is readable
    #
    # \return Boolean True/False
    def readable(self):
        return True
    
    ## Indicates the socket is writable
    #
    # \return Boolean True/False
    def writable(self):
        return self.is_writable
        
    ## Close connection handler
    #
    def handle_close(self):
        logging.debug("Disconnected")
        self.close()
    
    ## Reading socket handler
    #    
    # Reads and processes client data, and throws the proper signal with coordinates as parameters
    def handle_read(self):
        #format: 20 bytes in total. Size: intle:16
        #Incomming messages comes with 160 bytes..
        data0 = self.recv(160);
        if data0:            
            data = ConstBitStream(bytes=data0, length=160)
            #print "All: %s" % data.bin
            
            msize = data.read('intle:16')
            mtype = data.read('intle:16')
            mtime = data.read('intle:64')
            
            # RA: 
            ant_pos = data.bitpos
            ra = data.read('hex:32')
            data.bitpos = ant_pos
            ra_uint = data.read('uintle:32')
            
            # DEC:
            ant_pos = data.bitpos
            dec = data.read('hex:32')
            data.bitpos = ant_pos
            dec_int = data.read('intle:32')
            
            #______ Testing:
            # Sends back to Stellarium the received coordinates, in order to update the field of view indicator
            (sra, sdec, stime) = coords.eCoords2str(float("%f" % ra_uint), float("%f" % dec_int), float("%f" %  mtime))
            self.act_pos(coords.hourStr_2_rad(sra), coords.degStr_2_rad(sdec))
            #______ End Testing
            
            # Emits the signal with received equatorial coordinates (for use in external Qt Gui..)
            self.stell_pos_recv.emit("%f" % ra_uint, "%f" % dec_int, "%f" %  mtime)
    
    
    ## Updates the field of view indicator in Stellarium
    #
    # \param ra Right ascension in signed string format
    # \param dec Declination in signed string format
    def act_pos(self, ra, dec):
        (ra_p, dec_p) = coords.rad_2_stellarium_protocol(float(ra), float(dec))
        
        times = 10 #Number of times that Stellarium expects to receive new coords //Absolutly empiric..
        for i in range(times):
            self.move(ra_p, dec_p)
    
    ## Sends to Stellarium equatorial coordinates
    #
    #  Receives the coordinates in float format. Obtains the timestamp from local time
    #
    # \param ra Ascensión recta.
    # \param dec Declinación.
    def move(self, ra, dec):
        msize = '0x1800'
        mtype = '0x0000'
        aux_format_str = 'int:64=%r' % time()
        localtime = ConstBitStream(aux_format_str.replace('.', ''))
        
        sdata = ConstBitStream(msize) + ConstBitStream(mtype)
        sdata += ConstBitStream(intle=localtime.intle, length=64) + ConstBitStream(uintle=ra, length=32)
        sdata += ConstBitStream(intle=dec, length=32) + ConstBitStream(intle=0, length=32)

        self.buffer = sdata
        self.is_writable = True
        self.handle_write()
            
    ## Transmission handler
    #
    def handle_write(self):
        self.send(self.buffer.bytes)
        self.is_writable = False
    

## \brief Implementation of the server side communications for 'Stellarium Telescope Protocol'.
#
#  Each connection request generate an independent execution thread as instance of Telescope_Channel
class Telescope_Server(QtCore.QThread, asyncore.dispatcher):
    # @var stell_pos_recv
    # Proxy signal to the same name signal of the Telescope_Channel instance
    stell_pos_recv = QtCore.pyqtSignal(str, str, str) #Ra, Dec, Time
    
    ## Class constructor
    #
    # \param port Port to listen on
    # \param pos-signal Signal that will receive the coordinates to send to Stellarium
    def __init__(self, port=10001, pos_signal=None):
        asyncore.dispatcher.__init__(self, None)
        QtCore.QThread.__init__(self, None)
        self.tel = None
        self.port = port
        if pos_signal != None:
            pos_signal.connect(self.proxy_signal_sent)
        
    ## Starts thread
    #
    # Sets the socket to listen on
    def run(self):
        logging.info(self.__class__.__name__+" is running...")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('localhost', self.port))
        self.listen(1)
        self.connected = False
        asyncore.loop()
        
    ## Handles incomming connection
    #
    # Stats a new thread as Telescope_Channel instance, passing it the opened socket as parameter
    def handle_accept(self):
        self.conn, self.addr = self.accept()
        logging.debug('Connected: %s', self.addr)
        self.connected = True
        self.tel = Telescope_Channel(self.conn)
        self.tel.stell_pos_recv.connect(self.proxy_signal_recv)
        
    ## Proxy signal for receive and throw again the Telescope_Channel signal
    #
    # \param Right ascension
    # \param dec Declination
    # \param mtime Timestamp
    def proxy_signal_recv(self, ra, dec, mtime):
        self.stell_pos_recv.emit(ra, dec, mtime)
        
    ## Proxy signal for receive coordinates and send them to the Telescope_Channel threads
    #
    # \ra Right ascension
    # \dec Declination
    def proxy_signal_sent(self, ra, dec):
        if self.tel != None:
            self.tel.act_pos(ra, dec)
        
    ## Closes the connection
    #
    def close_socket(self):
        if self.connected:
            self.conn.close()

#Run a Telescope Server
if __name__ == '__main__':
    try:
        Server = Telescope_Server()
        Server.run()
    except KeyboardInterrupt:
        logging.debug("\nBye!")
