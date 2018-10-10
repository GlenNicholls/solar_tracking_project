function [AZ,EL,sn,sr,ss] = AZELCalculator(JDN,time,Lat,Long,TZ)
clc
%**************************************************************************
%**************************************************************************
%This function calculates the azimuth and elevation of the sun at anytime of the day corrected for
%atmospheric aberration and earth orbit eccentiricity.
%Variables passed in by the calling program
%   JDN - Julian Date Number
%   Lat - Local latitude
%   Long - Local Longitude (negative when west of the prime meridian)
%   TZ - Local time zone (negative west of the prime meridian
%Variable return by the function
%   AZ - Azimuth (deg)
%   EL - Elevation (deg)
%   sn - Solar noon (time value)
%   sr - Sunrise (time value)
%   ss - Sunset (time value)
%**************************************************************************
%**************************************************************************

rlat = Lat*pi/180; %Latitude (radians)
rlong = Long*pi/180;  %Longitude (radians)
jd = JDN+2415018.5+time-TZ/24; %Julian Date
jc = (jd-2451545)/36525; %Julian century
gml = mod(280.46646+jc*(36000.76983+jc*.0003032),360); %geometric mean longitude (deg)
rgml = gml*pi/180;
gma = 352.52911+jc*(35999.05029-jc*.0001557); %geometric mean anamoly (deg)
rgma = gma*pi/180;
eoe = .016708634-jc*(.000042037-jc*.0001551); %Earth orbit eccentricity
sec = sin(rgma)*(1.914602-.004817*jc)+sin(2*rgma)*(.01993-.000101*jc)*sin(3*rgma)*.000289; %Sun equation of center
stl = gml+sec; %Sun true longitude (deg)
rstl = stl*pi/180;
sta = gma+sec; %Sun true anomaly (deg)
rsta = sta*pi/180;
srv = (1.000001018*(1-eoe))/(1+eoe*cos(rsta)); %Sun radian vector
apl = stl-.00569-.00478*sin((125.04-1934.136*jc)*pi/180); %sun apparent longitude (deg)
rapl = apl*pi/180;
moe = 23+(26+((21.448-jc*(46.815*jc*(.00059-.001813*jc)))))/60/60; %Mean oblique eccliptic (deg)
rmoe = moe*pi/180;
oc = moe+.00256*cos((125.04-1934.136*jc)*pi/180); %Oblique correction (deg)
roc = oc*pi/180;
sra = atan2((cos(roc)*sin(rapl)),cos(rapl))*180/pi; %Sun right ascension (deg)
rsra = sra*pi/180;
rsdec = asin(sin(roc)*sin(rapl)); %Sun declination (deg)
sdec = rsdec*180/pi;
var = tan(roc/2)^2; %Sun variance
%equation of time
et = 4*(var*sin(2*rgml)-2*eoe*sin(rgma))*180/pi+4*eoe*var*sin(rgma)*cos(2*rgml)-.5*var^2*sin(4*rgml)-1.25*eoe^2*sin(2*rgma);
ras = acos(cos(90.833*pi/180)/(cos(rlat)*cos(rsdec))-tan(rlat)*tan(rsdec)); %Sunrise angle
as = ras*180/pi;
sn = (720-4*Long-et+TZ*60)/1440; %Solar noon
sr = sn-as*4/1440; %sunrise
ss = sn+as*4/1440; %Sunset
sd = 8*as; %Sun duration (minutes)
tst = mod(time*1440+et+4*Long-60*TZ,1440); %True solar time
%Hour angle
if tst/4<0
    ha = tst/4+180;
else
    ha = tst/4-180;
end
rha = ha*pi/180; 
rsz = acos(sin(rlat)*sin(rsdec)+cos(rlat)*cos(rsdec)*cos(rha)); %Solar zenith
sz = rsz*180/pi; 
sea = 90-sz; %Solar elevation angle
rsea = pi/2-rsz;
% Solar atmospheric refraction
if sea>85
    ref = 0;
elseif sea>5
    ref = (58.1/tan(rsea)-.07/(tan(rsea)^2)+.000086/tan(rsea)^5)/3600;
elseif sea>-.575
    ref = (1735+sea*(-518.2+sea*(103.4+sea*(-12.79+sea*.711))))/3600;
else
    ref = -20.772/tan(rsea)/3600;
end
%Elevation coordinate
EL = sea+ref;
%Azimuth coordinate
if ha>0
    AZ = mod(180/pi*(acos((sin(rlat)*cos(rsz)-sin(rsdec))/(cos(rlat)*sin(rsz))))+180,360);
else
    AZ = mod(540-180/pi*(acos( (sin(rlat)*cos(rsz)-sin(rsdec)) / (cos(rlat)*sin(rsz)) )),360);
end