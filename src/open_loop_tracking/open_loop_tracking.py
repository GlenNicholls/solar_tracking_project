from __future__ import division
from datetime import datetime
import time
# import jdcal # Julian dates from proleptic Gregorian and Julian calenders.
from math import pi, atan2
from math import sin
from math import cos
from math import tan
from math import radians
from math import degrees
from math import fmod
from math import asin
from math import acos
from math import pow


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



def AZELCalculator(JDN,time,Lat,Long,TZ):


    #**************************************************************************
    #**************************************************************************
    #This function calculates the azimuth and elevation of the sun at anytime of the day corrected for
    #atmospheric aberration and earth orbit eccentiricity.
    #Variables passed in by the calling program
    #   JDN - Julian Date Number
    #   Lat - Local latitude
    #   Long - Local Longitude (negative when west of the prime meridian)
    #   TZ - Local time zone (negative west of the prime meridian
    #Variable return by the function
    #   AZ - Azimuth (deg)
    #   EL - Elevation (deg)
    #   sn - Solar noon (time value)
    #   sr - Sunrise (time value)
    #   ss - Sunset (time value)
    #**************************************************************************
    #**************************************************************************

    rlat = Lat*pi/180 #Latitude (radians)
    rlong = Long*pi/180  #Longitude (radians)
    jd = JDN+2415018.5+time-TZ/24 #Julian Date
    jc = (jd-2451545)/36525 #Julian century
    gml = fmod(280.46646+jc*(36000.76983+jc*.0003032),360) #geometric mean longitude (deg)
    rgml = gml*pi/180
    gma = 352.52911+jc*(35999.05029-jc*.0001557) #geometric mean anamoly (deg)
    rgma = gma*pi/180
    eoe = .016708634-jc*(.000042037-jc*.0001551) #Earth orbit eccentricity
    sec = sin(rgma)*(1.914602-.004817*jc)+sin(2*rgma)*(.01993-.000101*jc)*sin(3*rgma)*.000289 #Sun equation of center
    stl = gml+sec #Sun true longitude (deg)
    rstl = stl*pi/180
    sta = gma+sec #Sun true anomaly (deg)
    rsta = sta*pi/180
    srv = (1.000001018*(1-eoe))/(1+eoe*cos(rsta)) #Sun radian vector
    apl = stl-.00569-.00478*sin((125.04-1934.136*jc)*pi/180); #sun apparent longitude (deg)
    rapl = apl*pi/180
    moe = 23+(26+((21.448-jc*(46.815*jc*(.00059-.001813*jc)))))/60/60 #Mean oblique eccliptic (deg)
    rmoe = moe*pi/180
    oc = moe+.00256*cos((125.04-1934.136*jc)*pi/180) #Oblique correction (deg)
    roc = oc*pi/180
    sra = atan2((cos(roc)*sin(rapl)),cos(rapl))*180/pi #Sun right ascension (deg)
    rsra = sra*pi/180
    rsdec = asin(sin(roc)*sin(rapl)) #Sun declination (deg)
    sdec = rsdec*180/pi
    var = pow(tan(roc/2),2) #Sun variance
    #equation of time
    et = 4*(var*sin(2*rgml)-2*eoe*sin(rgma))*180/pi+4*eoe*var*sin(rgma)*cos(2*rgml)-.5*pow(var,2)*sin(4*rgml)-1.25*pow(eoe,2)*sin(2*rgma)
    rsa = acos(cos(90.833*pi/180)/(cos(rlat)*cos(rsdec))-tan(rlat)*tan(rsdec)) #Sunrise angle
    sa = rsa*180/pi
    sn = (720-4*Long-et+TZ*60)/1440 #Solar noon
    sr = sn-sa*4/1440 #sunrise
    ss = sn+sa*4/1440 #Sunset
    sd = 8*sa #Sun duration (minutes)
    tst = fmod(time*1440+et+4*Long-60*TZ,1440) #True solar time
    #Hour angle
    if tst/4<0:
        ha = tst/4+180
    else:
        ha = tst/4-180

    rha = ha*pi/180
    rsz = acos(sin(rlat)*sin(rsdec)+cos(rlat)*cos(rsdec)*cos(rha)) #Solar zenith
    sz = rsz*180/pi
    sea = 90-sz #Solar elevation angle
    rsea = pi/2-rsz
    # Solar atmospheric refraction
    if sea > 85:
        ref = 0
    elif sea > 5:
        ref = ((58.1/tan(rsea)-.07)/(pow(tan(rsea),2)+.000086/pow(tan(rsea),5)))/3600
    elif sea > -.575:
        ref = (1735+sea*(-518.2+sea*(103.4+sea*(-12.79+sea*.711))))/3600
    else:
        ref = -20.772/tan(rsea)/3600

    #Elevation coordinate
    EL = sea+ref
    #Azimuth coordinate
    if ha>0:
        AZ = fmod(180/pi*(acos((sin(rlat)*cos(rsz)-sin(rsdec))/(cos(rlat)*sin(rsz))))+180,360)
    else:
        AZ = fmod(540-180/pi*(acos( (sin(rlat)*cos(rsz)-sin(rsdec)) / (cos(rlat)*sin(rsz)) )),360)

    return(AZ,EL,sn,sr,ss)

from time import localtime
import time

H = (int)(time.strftime('%H',localtime()))
M = (int)(time.strftime('%M',localtime()))
Y = (int)(time.strftime('%Y',localtime()))
Mo = (int)(time.strftime('%m',localtime()))
D = (int)(time.strftime('%d',localtime()))
TZ = (int)(time.strftime('%z',localtime()))/100
doy = (int)(time.strftime('%j',localtime()))
time = H/24+M/1400
Y,Mo,D,H,M,TZ


Lat = 38.89; #Entered Latitude
Long = -104.8 #Entered Longitude
time = H/24+M/1440
JDN = (Y-1900-29)*365+29*366+doy+1 #Julian Date Number based on year


AZnow,ELnow,noon,sunrise,sunset = AZELCalculator(JDN,time,Lat,Long,TZ)

AZsr,ELsr,_,_,_ = AZELCalculator(JDN,sunrise,Lat,Long,TZ)
AZss,ELss,_,_,_ = AZELCalculator(JDN,sunset,Lat,Long,TZ)
AZnoon,ELnoon,_,_,_ = AZELCalculator(JDN,noon,Lat,Long,TZ)
duration = sunset-sunrise
AZtotal = AZss-AZsr
ELtotal = (ELnoon-ELss)+(ELnoon-ELsr)
AZrate1 = AZtotal/duration #deg/min
ELrate1 = ELtotal/duration #deg/min
AZrate2 = duration/AZtotal #min/deg
ELrate2 = duration/ELtotal #min/deg


AZmove = (AZnow-60)*22.22
ELmove = ELnow*72.22
AZnow,ELnow
