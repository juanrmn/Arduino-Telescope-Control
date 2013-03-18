#include <stdio.h>
#include <string.h>
#include <math.h>
#include "CoordsLib.h"
#include "AxesLib.h"


/**
 * Output pin for the STEP on X axis of the stepper controller (horizontal)
 */
int stepperPin1 = 3;

/**
 * Output pin for the STEP on Y axis of the stepper controller (vertical)
 */
int stepperPin2 = 4;

/**
 * Output pin for the rotate direction of both axes 
 * (DIR pin of the stepper controllers)
 */
int steppersDir = 2;

/**
 * Enable the engine power supply of the X axis
 * (ENABLE pin of the controller)
 */
int enableStepper1 = 9;

/**
 * Enables the engine power supply of the Y axis
 * (ENABLE pin of the controller)
 */
int enableStepper2 = 10;

/**
 * Input pin for the end limit sensor of the X axis (360º)
 */
int sensor360H = 5;

/**
 * Input pin for the init limit sensor of the X axis (0º)
 */
int sensor0H = 11;

/**
 * Input pin for the bottom limit sensor of the Y axis (0º)
 */
int sensorBottomV = 6;

/**
 * Input pin for the top limit sensor of the Y axis (90º)
 */
int sensorTopV = 7;

/**
 * Output pin to control the laser pointer
 */
int laserPin = 8;

/**
 * Library for coordinates transformations
 */
CoordsLib Coords = CoordsLib();

/**
 * Library for control the device: stepper motors, sensors, current position..
 */
AxesLib	Axes = AxesLib();

/**
 * Initializes the serial port and sets pins to control the device
 */
void setup(){
	Serial.begin(9600);
	Serial.println("init");
	
	pinMode(laserPin, OUTPUT);
	laserOff();
	
	Axes.setMotorsPins(stepperPin1, stepperPin2, steppersDir, enableStepper1, enableStepper2);
	Axes.setSensorsPins(sensor0H, sensor360H, sensorBottomV, sensorTopV);
}

/**
 * Turn the laser On
 */
void laserOn(){
	digitalWrite(laserPin, LOW);
}

/**
 * Turn the laser Off
 */
void laserOff(){
	digitalWrite(laserPin, HIGH);
}

/*
 * Get a float value from the serial port, and send the '_OK_' ack string.
 * The value must conains six decimals, in a string with 9 bytes, including sign and decimal dot.
 * Examples: '-0.036526', '+5.238388'
 *
 * \return float.
 */
float serialGetFloat(){
	char bytes[9], sign;
	int nbytes = 0;
	float fex;
	bool recv = false;
	
	bytes[8] = '\0';
	Serial.println("float");
	while(!recv){
		if (Serial.available() > 0) {
			sign = Serial.read();//Float with eight representation bytes (including dot and sign)
			while(nbytes < 8)
				if(Serial.available() > 0){
					bytes[nbytes] = Serial.read();
					nbytes++;
				}
			fex = strtod(bytes, NULL);
			if(sign=='-')
				fex = 0.0 - fex;
			recv = true;
		}
	}
	Serial.println("_OK_");
	return fex;
}

/**
 * Main loop..
 *
 * Obtains and executes the commands received by the serial port
 * 
 * Avaliable commands:
 * 
 *-	'init' () -> (float px, float py)	Initializes the device and returns the steps by revolution obtained
 *- 'time' (float t)  -> ()		Sets initial observation time
 *- 'set1' (float ar, float dec, float t, float ac, float alt) -> ()	Sets the first reference object
 *-	'set2' (float ar, float dec, float t, float ac, float alt) -> ()	Sets the second reference object
 *-	'set3' (float ar, float dec, float t, float ac, float alt) -> ()	Sets the third reference object (usually not used..)
 *-	'goto' (float ar, float dec, float t) -> (float ar, float dec)(float ac, float alt)		Points the device towards the received equatorial coordinates
 *-	'move' () -> (float px, float py)(float ar, float dec)(float ac, float alt)		Points the device towards the received horizontal coordinates
 *-	'movx' (char dir) -> (float ar, float dec)(float ac, float alt)		Starts the accelerated horizontal movement towards the indicated direction
 *-	'movy' (char dir)	Starts the accelerated vertical movement towards the indicated direction
 *-	'stop' () -> ()		Stops the movements initiated by movx or movy commands
 *-	'laon' () -> ()		Turn the laser On
 *-	'loff' () -> ()		Turn the laser Off
 */
void loop(){
	float t0;
	float ar, dec, t;
	float ac, alt;
	char comm[5];
	char dir;
	int bytes_recv = 0;
	bool mov_end;

	comm[4]='\0';
	Serial.println("cmd");
	while(bytes_recv < 4){
		//Waiting for a command...
		if (Serial.available() > 0)
			comm[bytes_recv++] = Serial.read();
	}
	
	//Obtaining the expected parameters of the command
	if(strcmp(comm, "set1")==0 || strcmp(comm, "set2")==0 || strcmp(comm, "set3")==0 || strcmp(comm, "goto")==0){
		ar = serialGetFloat();
		dec = serialGetFloat();
		t = serialGetFloat();
	}
	if(strcmp(comm, "move")==0){
		ac = serialGetFloat();
		alt = serialGetFloat();
		t = serialGetFloat();
	}
	
	//Executing command
		
	if(strcmp(comm, "time")==0){
		t0 = serialGetFloat();
		Coords.setTime(t0);
		Serial.println();
		Serial.println("done_time");
	}else if(strcmp(comm, "set1")==0){	
		Coords.setRef_1(ar, dec, t, Axes.getX(), Axes.getY());
		Serial.println();
		Serial.println("done_set1");
	}else if(strcmp(comm, "set2")==0){		
		Coords.setRef_2(ar, dec, t, Axes.getX(), Axes.getY());
		Serial.println();
		Serial.println("done_set2");
	}else if(strcmp(comm, "set3")==0){		
		Coords.setRef_3(ar, dec, t, Axes.getX(), Axes.getY());
		Serial.println();
		Serial.println("done_set3");
	}else if(strcmp(comm, "goto")==0){
		Coords.getHCoords(ar, dec, t, &ac, &alt);
		Axes.goToRads(ac, alt);
		Serial.print("h_");Serial.print(Axes.getX(), 6); Serial.print(' '); Serial.print(Axes.getY(), 6);Serial.println();
		if(Coords.isConfigured()==true){
			Coords.getECoords(ac, alt, t, &ar, &dec);
			Serial.print("e_");Serial.print(ar, 6); Serial.print(' '); Serial.print(dec, 6);Serial.println();
        }
		Serial.println("done_goto");
	}else if(strcmp(comm, "move")==0){
		Axes.goToRads(ac, alt);
		Serial.print("p_");Serial.print(Axes.getPx(), DEC); Serial.print(' '); Serial.print(Axes.getPy(), DEC);Serial.println();
		Serial.print("h_");Serial.print(Axes.getX(), 6); Serial.print(' '); Serial.print(Axes.getY(), 6);Serial.println();
		if(Coords.isConfigured()==true){
			Coords.getECoords(ac, alt, t, &ar, &dec);
			Serial.print("e_");Serial.print(ar, 6); Serial.print(' '); Serial.print(dec, 6);Serial.println();
        }
		Serial.println("done_move");
	}else if(strcmp(comm, "movx")==0){
		while(Serial.available()<=0){}
		dir = Serial.read();
		mov_end = Axes.movx((dir == '1'));
		Serial.print("h_");Serial.print(Axes.getX(), 6); Serial.print(' '); Serial.print(Axes.getY(), 6);Serial.println();
		if(Coords.isConfigured()==true){
			Coords.getECoords(Axes.getX(), Axes.getY(), t, &ar, &dec);
			Serial.print("e_");Serial.print(ar, 6); Serial.print(' '); Serial.print(dec, 6);Serial.println();
        }
		if(mov_end==false)
			Serial.println("done_movx");
		else
			Serial.println("done_end");
	}else if(strcmp(comm, "movy")==0){
		while(Serial.available()<=0){}
		dir = Serial.read();
		mov_end = Axes.movy((dir == '1'));
		Serial.print("h_");Serial.print(Axes.getX(), 6); Serial.print(' '); Serial.print(Axes.getY(), 6);Serial.println();
		if(Coords.isConfigured()==true){
			Coords.getECoords(Axes.getX(), Axes.getY(), t, &ar, &dec);
			Serial.print("e_");Serial.print(ar, 6); Serial.print(' '); Serial.print(dec, 6);Serial.println();
        }
		if(mov_end==false)
			Serial.println("done_movy");
		else
			Serial.println("done_end");
	}else if(strcmp(comm, "init")==0){
		Axes.init();
		Serial.println();
		Serial.print("p_");Serial.print(Axes.getPX(), DEC); Serial.print(' '); Serial.print(Axes.getPY(), DEC);Serial.println();
		Serial.println("done_init");
	}else if(strcmp(comm, "laon")==0){
		laserOn();
		Serial.println();
		Serial.println("done_laserOn");
	}else if(strcmp(comm, "loff")==0){
		laserOff();
		Serial.println();
		Serial.println("done_laserOff");
	}else if(strcmp(comm, "stop")==0){
		Serial.println("done_stop");
	}else	
		Serial.println("ERROR");
}

