Y = 2018; %Entered year
M = 6;  %Entered month
D = 22; %Entered day
H = 4;  %Entered hour (1-23)
m = 36;  %Entered day (1-31)
Lat = 38.89; %Entered Latitude
Long = -104.8; %Entered Longitude
TZ = -7; %Entered Time Zone
time = H/24+m/1440;
JDN = (Y-1900-29)*365+29*366; %Julian Date Number based on year

%****************** Number of days by month ******************************
M1 = 31;
if mod(Y-1900,4) == 0
    M2 + 29;
else
    M2 = 28;
end
M3 = 31;
M4 = 30;
M5 = 31;
M6 = 30;
M7 = 31;
M8 = 31;
M9 = 30;
M10 = 31;
M11 = 30;
M12 = 31;
%*************************************************************************

%************************ Calculates the final JDN ***********************
switch M
    case 1
        JDN = JDN+D;
    case 2
        JDN = JDN+M1+D;
    case 3
        JDN = JDN+M1+M2+D;
    case 4
        JDN = JDN+M1+M2+M3+D;
    case 5
        JDN = JDN+M1+M2+M3+M4+D;
    case 6
        JDN = JDN+M1+M2+M3+M4+M5+D;
    case 7
        JDN = JDN+M1+M2+M3+M4+M5+M6+D;
    case 8
        JDN = JDN+M1+M2+M3+M4+M5+M6+M7+D;
    case 9
        JDN = JDN+M1+M2+M3+M4+M5+M6+M7+M8+D;
    case 10
        JDN = JDN+M1+M2+M3+M4+M5+M6+M7+M8+M9+D;
    case 11
        JDN = JDN+M1+M2+M3+M4+M5+M6+M7+M8+M9+M10+D;
    case 12
        JDN = JDN+M1+M2+M3+M4+M5+M6+M7+M8+M9+M10+M11+D;
end
JDN = JDN+1; %Julian Date Number
[AZ,EL,noon,sunrise,sunset] = AZELCalculator(JDN,time,Lat,Long,TZ);
[AZ1,EL1,noon,sunrise,sunset] = AZELCalculator(JDN,sunrise,Lat,Long,TZ);
[AZ2,EL2,noon, sunrise,sunset] = AZELCalculator(JDN,sunset,Lat,Long,TZ);
[AZn,ELn,noon,sunrise,sunset] = AZELCalculator(JDN,noon,Lat,Long,TZ);
duration = (sunset-sunrise)*1440;
AZtotal = AZ2-AZ1;
ELtotal = (ELn-EL2)+(ELn-EL1);
AZrate1 = AZtotal/duration; %deg/min
ELrate1 = ELtotal/duration; %deg/min
AZrate2 = duration/AZtotal %min/deg
ELrate2 = duration/ELtotal %min/deg
AZ
EL

