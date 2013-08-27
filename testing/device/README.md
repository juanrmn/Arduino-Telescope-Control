Testing Arduino software
---------------------------

Communications with the device and Coordinate transformations.

Sends commands and equatorial coordinates to the device, and receives the transformation results.

*Note that two reference objects are required for initial configuration in order to obtain the transformation
matrix.*


### Example of use

Data:

	Date and time: 	22:02 - August 9, 2012
	Lat:			N 37° 24' 0.01"
	Long:			W 5° 58' 48.00"
	
	__Obj__			__RA/DEC (J2000)__		__Time__	__Az/Alt__
	
	Polaris			2h31m49s/81º15'51''	22h04m20s 	0º27'09''/36º49'17''
	Vega			18h36m56s/38º47'03''	22h05m07s	78º10'04''/70º05'19''
	
	Altair			19h50m47s/8º52'07''	22h06m11s	114º36'45''/41º30'22''
	Lagoon Nebula	18h03m48s/-24º23'00''	22h06m52s	163º02'47''/26º15'16''
	Mars			13h17m55s/-8º29'04''	22h07m51s	240º18'46''/21º04'41''


Example with given data and the ipython console output _(Note the RECV lines with the results)_:

	In [1]: from testing import *

	In [2]: t = Testing()
	
	In [3]: t.init()
	
	In [4]: t.setTime("22h02m0s")
	
	In [5]: t.setRef(1 , "2h31m49s", "89º15'51''", "22h04m20s", "0º27'09''", "36º49'17''")
	SEND:	+0.662425/+1.557954 - +5.778494 - +0.007898/+0.642654
	
	In [6]: t.setRef(2 , "18h36m56s", "38º47'03''", "22h05m07s", "78º10'04''", "70º05'19''")
	SEND:	+4.873541/+0.676911 - +5.781912 - +1.364285/+1.223277
	
	In [7]: t.goto("19h50m47s", "8º52'07''", "22h06m11s")
	SEND:	+5.195772/+0.154786 - +5.786566
	RECV:	2.000384/0.724421	(114º36'49'' / 41º30'23'')
	
	In [8]: t.goto("18h03m48s", "-24º23'00''", "22h06m52s")
	SEND:	+4.728970/-0.425569 - +5.789548
	RECV:	2.845698/0.458214	(163º2'47'' / 26º15'13'')

	In [9]: t.goto("13h17m55s", "-8º29'04''", "22h07m51s")
	SEND:	+3.481568/-0.148081 - +5.793839
	RECV:	-2.088903/0.367851	(240º18'53'' / 21º4'35'')


([More info...](http://yoestuveaqui.es/blog/communications-between-python-and-arduino-usb-serial/))
