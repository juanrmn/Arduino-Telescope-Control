#ifndef AxesLib_h
#define AxesLib_h

	#include <math.h>
	#include <string.h>
	
	/**
	 * \brief Class that manages movements and the laser of the device
	 *
	 * Uses the stepper motors and sensors to positioning the device at a given horizontal coordinates, 
	 * within a range of 360º degrees in horizontal, and 180º on vertical.
	 * To the movements uses the DDA algorithm (Digital Differential Algorithm).
	 */
	class AxesLib{
		private:
			/**
			 * Pins to control the stepper motors
			 */
			int _stPin_x, _stPin_y, _dirPin, _enable_x, _enable_y;
			
			/**
			 * Steps per degree on each axis
			 */
			float _pgrad_x, _pgrad_y;
			
			/**
			 * Current position of each axis (in radians)
			 */
			float _rx, _ry;
			
			/**
			 * Auxiliary variables, maximum theoric values, and steps per revolution respectively
			 */
			int _x, _y, _X, _Y, _pv_x, _pv_y;
			
			/**
			 * Theoric central values of each axis
			 */
			int _revx, _topy;
			
			/**
			 * Indicates if X axis has been "reverted" (Y is between 90º and 180º)
			 */
			bool _x_rev;
			
			/**
			 * Sensor pins
			 */
			int _s0Pin_x, _s360Pin_x, _sbottomPin_y, _stopPin_y;
			
			/**
			 * Transforms radian to degrees
			 *
			 * \param rad Radians
			 * \return degrees
			 */
			int _rad2deg(float rad);
			
			/**
			 * Degrees to radians
			 *
			 * \param deg Degrees
			 * \return radians
			 */
			float _deg2rad(float deg);
			
			/**
			 * Moves one of the motors a given number of steps
			 *
			 * \param axis Pin of the motor to move
			 * \param dir Direction: True means clockwise direction on X, and upwards on Y
			 * \param steps Number of steps (if limit sensor is not reached)
			 * \param sensor Pin of the sensor that can be reached towards that direction
			 * \param nodelay Skip the initial delay (useful to DDA algorithm)
			 * \return Number of steps (distinct of the steps parameter if the sensor has been reached)
			 */
			int _step(int axis, bool dir, int steps, int sensor, bool nodelay=false);
			
			/**
			 * Enables the motors power supply
			 */
			void _enableMotors();
			
			/**
			 * Disables the motors power supply
			 */
			void _disableMotors();
			
			/**
			 * Moves the device to the given position
			 * 
			 * \param x Number of steps from 0 to the desired position on X axis
			 * \param y Number of steps from 0 to the desired position on Y axis
			 * \param method Algorithm selection: DDA or XY (first X axis, then Y), by default is DDA
			 */
			void _moveTo(int x, int y, char* method = "DDA");
			
			/**
			 * Moves the device to the given position, first X axis and then Y axis
			 * 
			 * \param x Number of steps from 0 to the desired position on X axis
			 * \param y Number of steps from 0 to the desired position on Y axis
			 * \param nodelay Omits the delay on changes of axis or direction
			 */
			void _moveXY(int x, int y, bool nodelay=false);
			
			/**
			 * Moves the device to the given position using DDA algorithm
			 * 
			 * \param x Number of steps from 0 to the desired position on X axis
			 * \param y Number of steps from 0 to the desired position on Y axis
			 */
			void _moveDDA(int x, int y);
			
		public:
			/**
			 * Class constructor
			 */
			AxesLib();
			
			/**
			 * Initializes the device
			 * 
			 * Along the process obtains the number of steps on each axis, and calculates the steps
			 * per degree for positioning
			 */
			void init();
			
			/**
			 * Returns current position on X axis
			 * 
			 * \return X position as radians
			 */
			float getX();
			
			/**
			 * Returns current position on Y axis
			 * 
			 * \return Y position as radians
			 */
			float getY();
			
			/**
			 * Return the number of steps per revolution of the X axis
			 *
			 * \return Steps per revolution
			 */
			int getPX();
			
			/**
			 * Number of steps from 0º to current position on X axis
			 *
			 * \return Current position on X
			 */
			int getPx();
			
			/**
			 * Return the number of steps per revolution of the Y axis
			 *
			 * \return Steps per revolution
			 */			
			int getPY();
			
			/**
			 * Number of steps from 0º to current position on Y axis
			 *
			 * \return Current position on Y
			 */
			int getPy();
			
			/**
			 * Sets the pins to control the stepper motors
			 *
			 * \param stPin_x Pin to move the X axis
			 * \param stPin_y Pin to move the Y axis
			 * \param dirPin Direction: True means clockwise direction on X axis, and downwards on Y
			 * \param enable_x Turn On/Off power supply on X axis motor
			 * \param enable_y Turn On/Off power supply on Y axis motor
			 */
			void setMotorsPins(int stPin_x, int stPin_y, int dirPin, int enable_x, int enable_y);
			
			/**
			 * Sets the pins connected to the sensors
			 *
			 * \param s0Pin_x Pin for the 0º limit sensor on X axis
			 * \param s360Pin_x Pir for the 360º limit sensor on X axis
			 * \param sbottomPin_y Pin for the 0º limit sensor on Y axis
			 * \param stopPin_y Sensor for the 90º limit sensor on Y axis
			 */			
			void setSensorsPins(int s0Pin_x, int s360Pin_x, int sbottomPin_y, int stopPin_y);
			
			/**
			 * Points the device towards the given coordinates
			 *
			 * \param rx Radians for the X axis, on range of 0 - 2*Pi
			 * \param ry Radians for the Y axis: on range of 0 - Pi
			 */				
			void goToRads(float rx, float ry);
			
			/**
			 * Accelerated movement for X axis
			 * 
			 * The movement stops when a 'stop' command is received by the serial port
			 *
			 * \param dir Direction: True means clockwise direction
			 * \return Returns true in case of reaches a limit sensor
			 */
			bool movx(bool dir);
			
			/**
			 * Accelerated movement for Y axis
			 * 
			 * The movement stops when a 'stop' command is received by the serial port
			 * 
			 * \param dir Direction: True means upwards
			 * \return Returns true in case of reaches a limit sensor
			 */
			bool movy(bool dir);
	};
#endif
