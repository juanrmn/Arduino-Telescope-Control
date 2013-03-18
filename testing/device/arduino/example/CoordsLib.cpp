// #include "WProgram.h" // Arduino < 1.0
#include <Arduino.h> //Arduino >= 1.0
#include "CoordsLib.h"

CoordsLib::CoordsLib(){
	_t0 = 0;
	_k =  1.002737908; // Constant.. Relationship between the solar time (M) and the sidereal time (S): (S = M * 1.002737908)
	_isSetR1 = false;
	_isSetR2 = false;
	_isSetR3 = false;
}

/*
 * Calculates the inverse of the m[3x3] matrix and returns it in the second parameter.
 */
void CoordsLib::_inv(float m[3][3], float res[3][3]){
	float idet;

	//Inverse of the determinant
	idet = 1/(
				(m[0][0]*m[1][1]*m[2][2]) + (m[0][1]*m[1][2]*m[2][0]) + (m[0][2]*m[1][0]*m[2][1])
			  -	(m[0][2]*m[1][1]*m[2][0]) - (m[0][1]*m[1][0]*m[2][2]) - (m[0][0]*m[1][2]*m[2][1]) 
			 );

	res[0][0] = ((m[1][1]*m[2][2]) - (m[2][1]*m[1][2]))*idet;
	res[0][1] = ((m[2][1]*m[0][2]) - (m[0][1]*m[2][2]))*idet;
	res[0][2] = ((m[0][1]*m[1][2]) - (m[1][1]*m[0][2]))*idet;

	res[1][0] = ((m[1][2]*m[2][0]) - (m[2][2]*m[1][0]))*idet;
	res[1][1] = ((m[2][2]*m[0][0]) - (m[0][2]*m[2][0]))*idet;
	res[1][2] = ((m[0][2]*m[1][0]) - (m[1][2]*m[0][0]))*idet;

	res[2][0] = ((m[1][0]*m[2][1]) - (m[2][0]*m[1][1]))*idet;
	res[2][1] = ((m[2][0]*m[0][1]) - (m[0][0]*m[2][1]))*idet;
	res[2][2] = ((m[0][0]*m[1][1]) - (m[1][0]*m[0][1]))*idet;
}

/*
 * Multiplies two matrices, m1[3x3] and m2[3x3], and returns the result in 
 * the third parameter.
 */
void CoordsLib::_m_prod(float m1[3][3], float m2[3][3], float res[3][3]){
	for(int i=0; i<3; i++)
		for(int j=0; j<3; j++){
			res[i][j] = 0.0;
			for(int k=0; k<3; k++) //multiplying row by column
				res[i][j] += m1[i][k] * m2[k][j];
		}
}

/*
 * Calculates the Vector cosines (EVC) from the equatorial coordinates (ar, dec, t).
 */
void CoordsLib::_setEVC(float ar, float dec, float t, float* EVC){
	EVC[0] = cos(dec)*cos(ar - _k*(t-_t0));
	EVC[1] = cos(dec)*sin(ar - _k*(t-_t0));
	EVC[2] = sin(dec);
}

/*
 * Calculates the Vector cosines (HVC) from the horizontal coordinates (ac, alt).
 */
void CoordsLib::_setHVC(float ac, float alt, float* HVC){
	HVC[0] = cos(alt)*cos(ac);
	HVC[1] = cos(alt)*sin(ac);
	HVC[2] = sin(alt);
}

/*
 * Sets the initial observation time.
 */
void CoordsLib::setTime(float t0){
	_t0 = t0;
}

/*
 * Sets the first reference object.
 * If all the reference objects have been established, calls the function that calculates T and iT.
 */
void CoordsLib::setRef_1(float ar, float dec, float t, float ac, float alt){
	_setEVC(ar, dec, t, _LMN1);
	_setHVC(ac, alt, _lmn1);
	_isSetR1 = true;
	_isSetR3 = false;

	if(_isSetR1 && _isSetR2 && _isSetR3)
		_setT();
}

/*
 * Sets the second reference object.
 * If all the reference objects have been established, calls the function that calculates T and iT.
 */
void CoordsLib::setRef_2(float ar, float dec, float t, float ac, float alt){
	_setEVC(ar, dec, t, _LMN2);
	_setHVC(ac, alt, _lmn2);
	_isSetR2 = true;
	_isSetR3 = false;

	if(_isSetR1 && _isSetR2 && _isSetR3)
		_setT();
}

/*
 * Sets the third reference object.
 * If all the reference objects have been established, calls the function that calculates T and iT.
 */
void CoordsLib::setRef_3(float ar, float dec, float t, float ac, float alt){
	_setEVC(ar, dec, t, _LMN3);
	_setHVC(ac, alt, _lmn3);
	_isSetR3 = true;

	if(_isSetR1 && _isSetR2 && _isSetR3)
		_setT();
}

/**
 * Indicates if the three reference objects have been established.
 */
bool CoordsLib::isConfigured(){
	return (_isSetR1 && _isSetR2 && _isSetR3);
}

/*
 * Third reference object calculated from the cross product of the two first ones.
 * Then calls the function that calculates T and iT.
 */
void CoordsLib::autoRef_3(){
	float sqrt1, sqrt2;

	if(_isSetR1 && _isSetR2){
		sqrt1 = (1/(  sqrt( pow(( (_lmn1[1]*_lmn2[2]) - (_lmn1[2]*_lmn2[1])),2) +
							pow(( (_lmn1[2]*_lmn2[0]) - (_lmn1[0]*_lmn2[2])),2) +
							pow(( (_lmn1[0]*_lmn2[1]) - (_lmn1[1]*_lmn2[0])),2))
				));
		_lmn3[0] = sqrt1 * ( (_lmn1[1]*_lmn2[2]) - (_lmn1[2]*_lmn2[1]) );
		_lmn3[1] = sqrt1 * ( (_lmn1[2]*_lmn2[0]) - (_lmn1[0]*_lmn2[2]) );
		_lmn3[2] = sqrt1 * ( (_lmn1[0]*_lmn2[1]) - (_lmn1[1]*_lmn2[0]) );

		sqrt2 = (1/(  sqrt( pow(( (_LMN1[1]*_LMN2[2]) - (_LMN1[2]*_LMN2[1])),2) +
							pow(( (_LMN1[2]*_LMN2[0]) - (_LMN1[0]*_LMN2[2])),2) +
							pow(( (_LMN1[0]*_LMN2[1]) - (_LMN1[1]*_LMN2[0])),2))
				));
		_LMN3[0] = sqrt2 * ( (_LMN1[1]*_LMN2[2]) - (_LMN1[2]*_LMN2[1]) );
		_LMN3[1] = sqrt2 * ( (_LMN1[2]*_LMN2[0]) - (_LMN1[0]*_LMN2[2]) );
		_LMN3[2] = sqrt2 * ( (_LMN1[0]*_LMN2[1]) - (_LMN1[1]*_LMN2[0]) );
		_isSetR3 = true;

		if(_isSetR1 && _isSetR2 && _isSetR3)
			_setT();
	}
}

/*
 *	Sets the transformation matrix and its inverse (T and iT, respectively).
 */
void CoordsLib::_setT(){
	float subT1[3][3], subT2[3][3], aux[3][3];

	subT1[0][0] = _lmn1[0]; subT1[0][1] = _lmn2[0]; subT1[0][2] = _lmn3[0];
	subT1[1][0] = _lmn1[1]; subT1[1][1] = _lmn2[1]; subT1[1][2] = _lmn3[1];
	subT1[2][0] = _lmn1[2]; subT1[2][1] = _lmn2[2]; subT1[2][2] = _lmn3[2];

	subT2[0][0] = _LMN1[0]; subT2[0][1] = _LMN2[0]; subT2[0][2] = _LMN3[0];
	subT2[1][0] = _LMN1[1]; subT2[1][1] = _LMN2[1]; subT2[1][2] = _LMN3[1];
	subT2[2][0] = _LMN1[2]; subT2[2][1] = _LMN2[2]; subT2[2][2] = _LMN3[2];

	_inv(subT2, aux);
	_m_prod(subT1, aux, _T);
	_inv(_T, _iT);
}

/*
 * Horizontal coordinates (ac, alt) obtained from equatorial ones and time (ar, dec, t).
 *
 * If the third reference object is not established, it calculates it by calling the 
 * proper function.
 */
void CoordsLib::getHCoords(float ar, float dec, float t, float *ac, float *alt){
	float HVC[3];
	float EVC[3];
	_setEVC(ar, dec, t, EVC);

	if(!_isSetR3)
		autoRef_3();

	for(int i=0; i<3; i++)
		HVC[i] = 0.0;
	for(int i=0; i<3; i++)
		for(int j=0; j<3; j++)
				HVC[i] += _T[i][j] * EVC[j];

	(*ac) = atan2(HVC[1], HVC[0]);
	(*alt) = asin(HVC[2]);
}

/*
 * Equatorial coordinates (ar, dec) obtained from horizontal ones and time (ac, alt, t).
 * 
 * If the third reference object is not established, it calculates it by calling the 
 * proper function.
 */
void CoordsLib::getECoords(float ac, float alt, float t, float *ar, float *dec){
	float HVC[3];
	float EVC[3];
	_setHVC(ac, alt, HVC);

	if(!_isSetR3)
		autoRef_3();

	for(int i=0; i<3; i++)
		EVC[i] = 0.0;
	for(int i=0; i<3; i++)
		for(int j=0; j<3; j++)
				EVC[i] += _iT[i][j] * HVC[j];

	(*ar) = atan2(EVC[1], EVC[0]) + (_k*(t-_t0));
	(*dec) = asin(EVC[2]);
}
