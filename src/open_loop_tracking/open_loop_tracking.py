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

        self._lat_rad  = latitude * pi / 180
        self._long_rad = longitude * pi / 180

