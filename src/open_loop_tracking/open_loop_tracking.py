from __future__ import division
from datetime import datetime
import time
import jdcal # Julian dates from proleptic Gregorian and Julian calenders. 


# REFERENCES: 


class open_loop_tracking(object):
    def __init__(self, latitude=34.6401861,
                       longitude=39.0494106,
                       local_time_zone='west'
                       ):

        self._lat_rad         = latitude * pi / 180
        self._long_rad        = longitude * pi / 180
        self._julian_date_num = jdcal
        self._tt              = datetime.now() # time tuple

        # todo: figure out num from time zone based on NOAA email mike sent
        # just use case or if statements to return self._time_zone for use with

    # get now time tuple
    # call this before running new calculation to ensure nothing changes
    def _get_time_tuple(self):
        self._tt = datetime.now()


    # get time
    # return H/24 + m/1440
    def _get_time(self):
        self._get_time_tuple()
        return self._tt.hour/24 + self._tt.minute/1440


    # Julian date number
    # based on date
    def _jul_date_num(self):
        # todo: incorporate Mike's switch from MATLAB somewhere in here
        year = self._tt.year
        print(year) # ensure thousands int like 2018 instead of 18
        return (year - 1900 - 29)*365 + 29*366


    # Julian Date
    def _jul_date(self):
        julian_date = self._jul_date_num() + 2415018.5 + self._get_time() - self._time_zone/24
        return julian_date


    # Julian century
    def _jul_century(self):
        return (self._jul_date() - 2451545)/36525


    # Geometric mean longitude
    # Return float(degrees)
    def _geo_mean_long_deg (self, jul_date):
        jc = self._jul_century()
        gml = 280.46646 + jc*(36000.76983 + jc*.0003032)
        gml = gml % 360
        return gml


    # Geometric mean longitude
    # Return rad
    def _geo_mean_long_rad (self):
        return self._geo_mean_long_deg()*pi/180


    # Geometric mean anomoly
    # return deg
    def _geo_mean_anomoly_deg (self):
        gma = 352.52911 + self._jul_century()*(35999.05029-self._jul_century()*.0001557)
        return gma


    # Geometric mean anomoly
    # return rad
    def _geo_mean_anomoly_rad (self):
        return self._geo_mean_anomoly_deg()*pi/180


    # Earth orbit eccentricity
    def _earth_orbit_eccentricity (self):
        eoe = .016708634-self._jul_century()*(.000042037-self._jul_century()*.0001551)
        return eoe


    # Sun equation of center ??
    # todo: figure out more about what this should be called
    def _sun_eqn_cntr (self):
        sec = sin(self._geo_mean_anomoly_rad())*(1.914602-.004817*self._jul_century())
        sec += sin(2*self._geo_mean_anomoly_rad())*(.01993-.000101*self._jul_century()) \ 
               *sin(3*self._geo_mean_anomoly_rad())*.000289
        return sec


    # true sun longitude
    # return deg
    def _true_sun_long_deg (self):
        return self._geo_mean_long_deg()+self._sun_eqn_cntr()


    # true sun longitude
    # return rad
    def _true_sun_long_rad (self):
        return self._true_sun_long_deg()*pi/180


    # true sun anomaly
    # return deg
    def _true_sun_anomaly_deg (self):
        return self._geo_mean_anomoly_deg()+self._sun_eqn_cntr()


    # true sun anomaly
    # return rad
    def _true_sun_anomaly_rad (self):
        return self._true_sun_anomaly_deg()*pi/180


    # sun radian vector
    def _sun_rad_vector (self):
        srv = (1.000001018*(1-self._earth_orbit_eccentricity())) / \
               (1+self._earth_orbit_eccentricity()*cos(self._true_sun_anomaly_rad()))
        return srv


    # apparent sun longitude
    # return deg
    def _apparent_sun_long_deg (self):
        asl = self._true_sun_long_deg() - .00569 - \
              .00478*sin((125.04-1934.136*self._jul_century())*pi/180)
        return asl


    # apparent sun longitude
    # return rad
    def _apparent_sun_long_rad (self):
        return self._apparent_sun_long_deg()*pi/180


    # Mean oblique eccliptic
    # return deg
    def _mean_oblique_eccliptic_deg (self):
        moe = 23+(26+((21.448-self._jul_century()*(46.815*self._jul_century()*(.00059-.001813*jc)))))/60/60
        return moe


    # Mean oblique eccliptic
    # return rad
    def _mean_oblique_eccliptic_rad (self):
        return self._mean_oblique_eccliptic_deg()*pi/180


    # Oblique correction
    # todo: is this already returning radians???
    # return deg
    def _oblique_correction_deg (self):
        oc = self._mean_oblique_eccliptic_deg()+.00256*cos((125.04-1934.136*self._jul_century())*pi/180)
        return oc


    # Oblique correction
    # return rad
    def _oblique_correction_rad (self):
        return self._oblique_correction_deg()*pi/180


    # Sun right ascension
    # return deg
    def _sun_right_ascension_deg (self):
        sra = atan2((cos(self._oblique_correction_rad())*sin(self._apparent_sun_long_rad())),cos(self._apparent_sun_long_rad()))*180/pi
        return sra


    # Sun right ascension
    # return rad
    def _sun_right_ascension_rad (self):
        return self._sun_right_ascension_deg()*pi/180


    # Sun declination
    def _sun_declination_rad (self):
