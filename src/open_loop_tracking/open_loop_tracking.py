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


    # Geometric mean longitude
    # Return float(degrees)
    def _geo_mean_long_deg(self, jul_date):

