#ifndef CoordsLib_h
#define CoordsLib_h

	#include <math.h>

	/**
	 * \brief Library for coordinates transformations. Calculates the equivalent coordinates between both coordinate systems equatorial and horizontal.
	 *
	 * It's based on Toshimi Taki's matrix method for coordinates transformation: http://www.geocities.jp/toshimi_taki/matrix/matrix.htm
	 * Contains the necessary methods for setting the initial time, the reference objects, the transformation matrix, and to 
	 * calculate the equivalent vectors between both coordinate systems.
	 */
	class CoordsLib{
		private:

			/**
			 * Constant of multiplication for the solar and sidereal time relation.
			 */
			float _k;

			/**
			 * Initial timestamp for the observations.
			 */			
			float _t0;

			/**
			 * Indicators for definition of the three reference objects.
			 */
			bool _isSetR1, _isSetR2, _isSetR3;

			/**
			 * Auxiliary matrices.
			 */
			float _lmn1[3], _LMN1[3], _lmn2[3], _LMN2[3], _lmn3[3], _LMN3[3];

			/**
			 * Transformation matrix. Transform vectors from equatorial to horizontal system.
			 */
			float _T[3][3];

			/**
			 * Inverse transformation matrix. Transform vectors from horizontal to equatorial system.
			 */
			float _iT[3][3];

			/**
			 * If the three reference objects have been defined, it calculates the transformation matrix from them.
			 */
			void _setT();

			/**
			 * Obtains a vector in polar notation from the equatorial coordinates and the observation time.
			 *
			 * \param ar Right ascension.
			 * \param dec Declination.
			 * \param t Timestamp of the observation.
			 * \param *EVC Pointer to array: Returns the three dimensional vector in polar notation.
			 */
			void _setEVC(float ar, float dec, float t, float* EVC);

			/**
			 * Obtains a vector in polar notation from the horizontal coordinates and observation time.
			 *
			 * \param ac Azimuth.
			 * \param alt Altitude.
			 * \param t Timestamp of the observation.
			 * \param *HVC Pointer to array: Returns the three dimensional vector in polar notation.
			 */			
			void _setHVC(float ac, float alt, float* HVC);

			/**
			 * Calculates the 3x3 inverse matrix.
			 * 
			 * \param m[3][3] Input matrix.
			 * \param res[3][3] Pointer to array: Returns the inverse matrix.
			 */
			void _inv(float m[3][3], float res[3][3]);

			/**
			 * Calculates the product of 3x3 matrices.
			 * 
			 * \param m1[3][3] Input matrix 1.
			 * \param m2[3][3] Input matrix 2.
			 * \param res[3][3] Pointer to array: Returns the result matrix.
			 */
			void _m_prod(float m1[3][3], float m2[3][3], float res[3][3]);

		public:

			/**
			 * Class constructor.
			 */
			CoordsLib();

			/**
			 * Sets the initial time.
			 *
			 * This parameter is used in order to consider time passing on horizontal coordinates system.
			 *
			 * \param t0 Unix Timestamp of the initial observation time.
			 */
			void setTime(float t0);

			/**
			 * Sets the first reference object from the coordinates in both coordinates systems for 
			 * that object.
			 *
			 * \param ar Right Ascension (equatorial coordinates).
			 * \param dec Declination (equatorial coordinates).
			 * \param t Unix Timestamp of the Observation.
			 * \param ac Azimuth (horizontal coordinates).
			 * \param alt Altitude (horizontal coordinates).
			 */
			void setRef_1(float ar, float dec, float t, float ac, float alt);

			/**
			 * Sets the second reference object from the coordinates in both coordinates systems for 
			 * that object.
			 *
			 * \param ar Right Ascension (equatorial coordinates).
			 * \param dec Declination (equatorial coordinates).
			 * \param t Unix Timestamp of the Observation.
			 * \param ac Azimuth (horizontal coordinates).
			 * \param alt Altitude (horizontal coordinates).
			 */
			void setRef_2(float ar, float dec, float t, float ac, float alt);

			/**
			 * Sets the third reference object from the coordinates in both coordinates systems for 
			 * that object.
			 *
			 * \param ar Right Ascension (equatorial coordinates).
			 * \param dec Declination (equatorial coordinates).
			 * \param t Unix Timestamp of the Observation.
			 * \param ac Azimuth (horizontal coordinates).
			 * \param alt Altitude (horizontal coordinates).
			 */
			void setRef_3(float ar, float dec, float t, float ac, float alt);

			/**
			 * Indicates if the three reference objects has been calculated.
			 * 
			 * \return Boolean.
			 */
			bool isConfigured();

			/**
			 * Third reference object calculated from the two others ones.
			 * 
			 * Calculates the cross product of the two first reference objects in both coordinates systems, in order 
			 * to obtain the third one.
			 * These two first objects must have 90º from each other, approximately (from 60º to 120º is enough to obtain
			 * goods results).
			 */
			void autoRef_3();

			/**
			 * Horizontal coordinates calculated from the equatorial ones and time.
			 *
			 * \param ar Right Ascension (equatorial coordinates).
			 * \param dec Declination (equatorial coordinates)
			 * \param t Unix Timestamp of the Observation.
			 * \param *ac Pointer to float: Returns the azimuth (horizontal coordiantes).
			 * \param *alt Pointer to float: Returns the altitude (horizontal coordinates).
			 */
			void getHCoords(float ar, float dec, float t, float *ac, float *alt);

			/**
			 * Equatorial coordinates calculated from the horizontal ones and time.
			 *
			 * \param ac Azimuth (horizontal coordinates).
			 * \param alt Altitude (horizontal coordinates).
			 * \param t Unix Timestamp of the Observation.
			 * \param *ar Pointer to float: Returns the right ascension (equatorial coordinates).
			 * \param *dec Pointer to float: Returns the declination (equatorial coordinates).
			 */
			void getECoords(float ac, float alt, float t, float *ar, float *dec);
	};

#endif
