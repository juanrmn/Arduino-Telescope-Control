#include <stdio.h>
#include <string.h>
#include <math.h>
#include "CoordsLib.h" //Library for coordinate conversion

CoordsLib Coords = CoordsLib();

void setup(){
	Serial.begin(9600);
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
			sign = Serial.read();
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

/*
 * Main loop.
 * 
 * 
 */
void loop(){
	float t0;
	float ar, dec, t;
	float ac, alt;
	char comm[5];
	int bytes_recv = 0;

	comm[4]='\0';
	Serial.println("cmd");
	while(bytes_recv < 4){
		//Waiting for a new command...
		if (Serial.available() > 0)
			comm[bytes_recv++] = Serial.read();
	}

	//Getting the command params (float values). The number of params depends on the command:
	if(strcmp(comm, "set1")==0 || strcmp(comm, "set2")==0 || strcmp(comm, "goto")==0){
		ar = serialGetFloat();
		dec = serialGetFloat();
		t = serialGetFloat();
	}
	if(strcmp(comm, "set1")==0 || strcmp(comm, "set2")==0){
		ac = (2 * M_PI - serialGetFloat()); //The Azimuth is measured in opposite direction of the Right Ascension
		alt = serialGetFloat();
	}

	//Processing command, and returning results and ack by the serial port:
	if(strcmp(comm, "time")==0){
		t0 = serialGetFloat();
		Coords.setTime(t0);
		Serial.println();
		Serial.println("done_time");
	}else if(strcmp(comm, "set1")==0){	
		Coords.setRef_1(ar, dec, t, ac, alt);
		Serial.println();
		Serial.println("done_set1");
	}else if(strcmp(comm, "set2")==0){		
		Coords.setRef_2(ar, dec, t, ac, alt);
		Serial.println();
		Serial.println("done_set2");
	}else if(strcmp(comm, "goto")==0){
		Coords.getHCoords(ar, dec, t, &ac, &alt);
		Serial.println();Serial.print((0.0 - ac), 6); Serial.print(' '); Serial.print(alt, 6);Serial.println();
		Serial.println("done_goto");
	}
}
