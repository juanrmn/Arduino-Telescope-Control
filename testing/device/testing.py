#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import math
import serial
from string import replace

## \brief Class for testing purposes..
#
#  Implements the set of available commands to send to the device (Arduino).
#  Also prints both sent data and results received from Arduino.
#  Includes some useful functions to units transformation (degrees, hours, radians..).
#
#  An example of use would be as follows:
#
#	from testing import *
#	t = Testing()
#	t.init()
#	t.setTime("22h02m0s")
#	t.setRef(1 , "2h31m49s", "89º15'51''", "22h04m20s", "0º27'09''", "36º49'17''")
#	t.setRef(2 , "18h36m56s", "38º47'03''", "22h05m07s", "78º10'04''", "70º05'19''")
#
#	t.goto("19h50m47s", "8º52'07''", "22h06m11s")
#	t.goto("18h03m48s", "-24º23'00''", "22h06m52s")
#	t.goto("13h17m55s", "-8º29'04''", "22h07m51s")
#
#
class Testing():
	def __init__(self, usb_serial='/dev/ttyUSB0', usb_serial_baud=9600, timeout=2):
		self.serial = serial.Serial(usb_serial, usb_serial_baud, timeout=timeout)

	def sread(self):
		line = self.serial.readline().rstrip()
		exp = re.compile('^((done.*$)|(cmd))$')
		return line

	def setTime(self, time):
		self.serial.write("time")
		resp = self.sread()
		if(resp == 'float'):
			self.serial.write(self.hours2rad(time))
			while(resp != 'cmd'):
				resp = self.sread()

	def init(self):
		exp = re.compile('^(-?)[0-9]{1,9} (-?)[0-9]{1,9}$')
		self.serial.write('init')
		resp = self.sread()
		while(resp != 'cmd'):
			if(exp.match(resp)):
				resp_d = resp.split(' ')
				print "(%s / %s)" % (resp_d[0], resp_d[1])
			resp = self.sread()

	def movx(self, signDir):
		self.serial.write('movx')
		self.serial.write(signDir)
	def movy(self, signDir):
		self.serial.write('movy')
		self.serial.write(signDir)
	def stop(self):
		exp = re.compile('^h_.*$')
		self.serial.write('stop')
		resp = self.sread()
		while(resp != 'done'):
			if(exp.match(resp)):
				resp = resp.replace("h_", '')
				resp_d = resp.split(' ')
				print "(%s / %s)" % (resp_d[0], resp_d[1])
			resp = self.sread()

	def setRef(self, id_ref, ra, dec, time, ac, alt):
		setf = {1: 'set1', 2: 'set2', 3: 'set3'}

		self.serial.write(setf[id_ref])
		resp = self.sread()
		if(resp == 'float'):
			self.serial.write(self.hours2rad(ra))
			self.serial.write(self.deg2rad(dec))
			self.serial.write(self.hours2rad(time))
			self.serial.write(self.deg2rad(ac))
			self.serial.write(self.deg2rad(alt))
			print "SEND:	%s/%s - %s - %s/%s" % (self.hours2rad(ra), self.deg2rad(dec), self.hours2rad(time), self.deg2rad(ac), self.deg2rad(alt))
			while(resp != 'cmd'):
				resp = self.sread()

	def goto(self, ra, dec, time):
		exp = re.compile('^(-?)[0-9]{1}.[0-9]{4,8} (-?)[0-9]{1}.[0-9]{4,8}$')
		self.serial.write('goto')
		resp = self.sread()
		if(resp == 'float'):
			self.serial.write(self.hours2rad(ra))
			self.serial.write(self.deg2rad(dec))
			self.serial.write(self.hours2rad(time))
			print "SEND:	%s/%s - %s" % (self.hours2rad(ra), self.deg2rad(dec), self.hours2rad(time))
			while(resp != 'cmd'):
				if(exp.match(resp)):
					resp_d = resp.split(' ')
					print "RECV:	%s/%s	(%s / %s)" % (resp_d[0], resp_d[1], self.rad2deg(resp_d[0]), self.rad2deg(resp_d[1]))
				resp = self.sread()

	# h =  HhMmSs => H+(M/60)+(S/60^2) hours
	# From hours to radians: (nhours * 15 * pi)/180
	def hours2rad(self, h):
		exp = re.compile('^[0-9]{,3}h[0-9]{,3}m[0-9]{,3}s$')
		if(not exp.match(h)):
			return None

		h = h.replace('h','.').replace("m",'.').replace("s",'.')
		h_dic = h.split('.')

		h_h = float(h_dic[0])
		h_m = float(h_dic[1])
		h_s = float(h_dic[2])

		nh = (h_h+(h_m/60)+(h_s/(60**2)))

		res = round((nh * 15 * math.pi) / 180, 6)
		if(res < 0.0): return '%f' % res;
		else: return '+%f' % res;

	# d = DºM'S'' => D+(M/60)+(S/60^2) degrees || D.dº
	# From degrees to radians: (ndeg * pi)/180
	def deg2rad(self, d):
		exp1 = re.compile('^-?[0-9]{,3}(º|ᵒ)[0-9]{,3}'[0-9]{,3}([']{2}|")$')
		exp2 = re.compile('^-?[0-9]{,3}.[0-9]{,6}(º|ᵒ)$')

		if(not exp1.match(d) and not exp2.match(d)):
			return None
		elif(exp1.match(d)):
			d = d.replace('º','.').replace("''",'.').replace("'",'.')
			d_dic = d.split('.')
			d_deg = float(d_dic[0])
			d_min = float(d_dic[1])
			d_sec = float(d_dic[2])

			if(d_deg < 0):
				d_min = 0 - d_min;
				d_sec = 0 - d_sec;

			d_ndeg = (d_deg+(d_min/60)+(d_sec/(60**2)))
		else:
			d_ndeg = float(d.replace('º',''))
			if(d_ndeg < 0): d_ndeg = 360 - abs(d_ndeg);

		res = round((d_ndeg * math.pi) / 180, 6)
		if(res < 0): return '%f' % res;
		else: return '+%f' % res;

	# DºM'S''
	# From radians to degrees: (rad * 180)/pi
	def rad2deg(self, rad):
		exp = re.compile('^(-?)[0-9]{1}.[0-9]{4,8}')

		if(not exp.match(rad)):
			return None

		r = float(rad)
		if(r < 0):
			r = (2 * math.pi) - abs(r)

		ndeg = (r * 180) / math.pi
		deg = math.floor(float(ndeg))
		nmins = (ndeg - deg) * 60
		mins = math.floor(nmins)
		secs = round( (nmins - mins) * 60 )

		return "%dº%d'%d''" % (deg, mins, secs)
