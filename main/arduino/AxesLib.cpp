// #include "WProgram.h" // Arduino < 1.0
#include <Arduino.h> //Arduino >= 1.0
#include "AxesLib.h"

AxesLib::AxesLib(){}

void AxesLib::setMotorsPins(int stPin_x, int stPin_y, int dirPin, int enable_x, int enable_y){
	_stPin_x = stPin_x;
	_stPin_y = stPin_y;
	_dirPin = dirPin;
	_enable_x = enable_x;
	_enable_y = enable_y;
	
	pinMode(_stPin_x, OUTPUT);
	pinMode(_stPin_y, OUTPUT);
	pinMode(_dirPin, OUTPUT);
	pinMode(_enable_x, OUTPUT);
	pinMode(_enable_y, OUTPUT);
}

void AxesLib::setSensorsPins(int s0Pin_x, int s360Pin_x,int sbottomPin_y, int stopPin_y){
	_s0Pin_x = s0Pin_x;	 			//0º sensor (the limit on counter clockwise direction on X axis)
	_s360Pin_x = s360Pin_x;	 		//360º sensor (he limit on clockwise direction on X axis..)
	_sbottomPin_y = sbottomPin_y;	//0º sensor (Y axis..)
	_stopPin_y = stopPin_y;			//90º sensor
	
	pinMode(_s0Pin_x, INPUT);
	pinMode(_s360Pin_x, INPUT);
	pinMode(_sbottomPin_y, INPUT);
	pinMode(_stopPin_y, INPUT);
}

void AxesLib::_enableMotors(){
	digitalWrite(_enable_x, LOW);
	digitalWrite(_enable_y, LOW);
}
void AxesLib::_disableMotors(){
	digitalWrite(_enable_x, HIGH);
	digitalWrite(_enable_y, HIGH);
}

void AxesLib::init(){
	//Here we supposes that 10000 steps are much more than one revolution.. 
	//(anyway, this number can be arbitrarily bigger)
	int MAX_STEPS = 10000;

	//We are on (0,0)
	_x = 0;
	_X = 0;
	_x_rev = false;
	_y = 0;
	_rx = 0.0;
	_ry = 0.0;
	
	_enableMotors();

	//Go to the 360º limit
	_step(_stPin_x, true, MAX_STEPS, _s360Pin_x);
	//Once there, count steps until the beginnin..
	_pv_x = _step(_stPin_x, false, MAX_STEPS, _s0Pin_x);
	_pgrad_x = (float) _pv_x/360;
	
	//The same procedure but for Y axis..
	_step(_stPin_y, true, MAX_STEPS, _stopPin_y);
	_pv_y = _step(_stPin_y, false, MAX_STEPS, _sbottomPin_y);
	_pgrad_y = (float) _pv_y/90;

	_disableMotors();

	//Maximum values
	_X = (360*_pgrad_x);
	_Y = (180*_pgrad_y);
	//Auxiliary values in case of Y > 90º
	_revx = 180*_pgrad_x;
	_topy = 90*_pgrad_y;
}

int AxesLib::_step(int axis, bool dir, int steps, int sensor, bool nodelay){
	int aux_x;
	
	//here, false value means clockwise..
	dir = !dir;
	
	//Because the device construction, the Y axis goes in opposite direction than X
	if(axis==_stPin_y)
		dir = !dir;
	digitalWrite(_dirPin,dir);
	
	if(nodelay == false)
		delay(50);
	for(int i=0;i<steps;i++){
		digitalWrite(axis, HIGH);
		delayMicroseconds(1200);
		digitalWrite(axis, LOW);
		delayMicroseconds(1200);
		
		//HIGH = limit reached on X   /   LOW = limit reached on Y
		if( (axis==_stPin_y && digitalRead(sensor)==LOW) || (axis==_stPin_x && digitalRead(sensor)==HIGH))
			return i+1;
	}
	return steps;
}

bool AxesLib::movx(bool dir){
	int steps = 0;
	char comm[5]="nost";
	int bytes_recv = 0;
	int facel = 7100;
	
	_enableMotors();
	
	//from here, false value means clockwise..
	dir = !dir;
	
	digitalWrite(_dirPin,dir);
	
	while(strcmp(comm, "stop")!=0){
		if( (dir==false && digitalRead(_s360Pin_x)==HIGH) || (dir && digitalRead(_s0Pin_x)==HIGH) )
			break;
		
		digitalWrite(_stPin_x, HIGH);
		delayMicroseconds(facel);
		digitalWrite(_stPin_x, LOW);
		delayMicroseconds(facel);
		
		steps++;

		if(steps % 50 == 0 && facel > 1100)
			facel -= 1000;
		
		while(Serial.available() > 0)
			comm[bytes_recv++] = Serial.read();
		//Safeguard...
		if(bytes_recv>4)
			break;
	}
	_disableMotors();
	
	if( dir )	_x -= steps;
	else		_x += steps;
	if(_x<0)	_x = 0;
	if(_x>_X)	_x = _X;
	if( (dir==false && digitalRead(_s360Pin_x)==HIGH) || (dir && digitalRead(_s0Pin_x)==HIGH) )
		return true;
	return false;
}
bool AxesLib::movy(bool dir){
	int steps = 0;
	char comm[5]="nost";
	int bytes_recv = 0;
	int facel = 7100;
	
	_enableMotors();
	
	//false value means upwards
	digitalWrite(_dirPin,dir);
	
	while(strcmp(comm, "stop")!=0){
		if( (dir && digitalRead(_stopPin_y)==LOW) || (dir==false && digitalRead(_sbottomPin_y)==LOW) )
			break;
		
		digitalWrite(_stPin_y, HIGH);
		delayMicroseconds(facel);
		digitalWrite(_stPin_y, LOW);
		delayMicroseconds(facel);
		
		steps++;
		
		if(steps % 50 == 0 && facel > 1100)
			facel -= 1000;
		
		while(Serial.available() > 0)
			comm[bytes_recv++] = Serial.read();
		//Safeguard...
		if(bytes_recv>4)
			break;
	}
	_disableMotors();
	
	if( dir )	_y += steps;
	else		_y -= steps;
	if(_y<0)	_y = 0;
	if(_y>_Y)	_y = _Y;
	if( (dir && digitalRead(_stopPin_y)==LOW) || (dir==false && digitalRead(_sbottomPin_y)==LOW) )
		return true;
	return false;
}

float AxesLib::getX(){
	float degx;
	
	if(_x_rev==false)	degx = (float) _x/_pgrad_x;
	else{
		if(_x>=_revx)
			degx = (float) (_x-_revx)/_pgrad_x;
		else
			degx = (float) (_x+_revx)/_pgrad_x;
	}
	_rx = _deg2rad(360.0 - degx);
	return _rx;
}

float AxesLib::getY(){
	if(_x_rev==false)
		_ry = _deg2rad((float) _y/_pgrad_y);
	else
		_ry = _deg2rad((float) (_topy+(_topy-_y))/_pgrad_y);
	return _ry;
}

int AxesLib::getPX(){
	return _pv_x;
}

int AxesLib::getPx(){
	return _x;
}

int AxesLib::getPY(){
	return _pv_y*4;
}

int AxesLib::getPy(){
	return _y;
}

int AxesLib::_rad2deg(float rad){
	return lrint( (float) (rad * 180.0)/M_PI );
}

float AxesLib::_deg2rad(float deg){
	return (float) (deg * M_PI)/ 180;
}

void AxesLib::goToRads(float rx, float ry){
	float degsH = (360.0 - _rad2deg(rx));
	if(degsH >= 360.0)
		degsH = degsH - 360.0;
	
	_moveTo((float) degsH*_pgrad_x, (float) _rad2deg(ry)*_pgrad_y);
}

void AxesLib::_moveTo(int x, int y, char* method){
	_enableMotors();
	
	if(x<0)	x = _X - fabs(x);
	if(0<0) y = 0;
	if(x>_X) x = _X;
	if(y>_Y) y = _Y;
	
	//Lets see if X axis has been "reverted" previously..
	if(y>_topy && _x_rev==false){
		_x_rev = true;
		y = _topy - (y-_topy);
		if(x>=_revx)	x = x-_revx;
		else			x = x+_revx;
	}else if(y>_topy && _x_rev){
		y = _topy - (y-_topy);
		if(x>=_revx)	x = x-_revx;
		else			x = x+_revx;
	}else if(_x_rev)
		_x_rev = false;
	
	if(strcmp(method, "DDA")==0)
		_moveDDA(x, y);
	else if(strcmp(method, "XY")==0)
		_moveXY(x, y);
	
	_disableMotors();
}

void AxesLib::_moveXY(int x, int y, bool nodelay){
	if(x>_x)
		_x += _step(_stPin_x, (x>_x), (x-_x), _s360Pin_x, nodelay);
	else
		_x -= _step(_stPin_x, (x>_x), (_x-x), _s0Pin_x, nodelay);
	
	if(y>_y)
		_y += _step(_stPin_y, (y>_y), (y-_y), _stopPin_y, nodelay);
	else
		_y -= _step(_stPin_y, (y>_y), (_y-y), _sbottomPin_y, nodelay);
}

void AxesLib::_moveDDA(int x, int y){
	int dx, dy, steps;
	float x_inc, y_inc, x_, y_;
	
	dx = x-_x;
	dy = y-_y;
	
	if(fabs(dx)>fabs(dy))
		steps = fabs(dx);
	else
		steps = fabs(dy);
		
	x_inc = (float) dx/steps;
	y_inc = (float) dy/steps;
	x_ = _x;
	y_ = _y;
	
	for(int i=1; i<steps+1; i++){
		x_ = x_+x_inc;
		y_ = y_+y_inc;
		_moveXY(lrint(x_), lrint(y_), true);
	}
}

