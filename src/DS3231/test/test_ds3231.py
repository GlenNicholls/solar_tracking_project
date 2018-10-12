import sys
import time
import datetime
import DS3231
import system_monitor


starttime = datetime.datetime.utcnow()

# create RTC object
i2c_port  = 1 # set to 0 if using gen 1 pi
i2c_addr  = 0x68
latitude  = 39.7392
longitude = 104.9903
rtc = DS3231.DS3231(i2c_port  = i2c_port,
                    i2c_addr  = i2c_addr,
                    latitude  = latitude,
                    longitude = longitude)

# create system monitor object
sys_mon = system_monitor.system_monitor()

print('-I- Monitoring DS3231 Information')

# Configure RTC
rtc.configure_rtc()

# Initial checks for time accuracy
print('-I- Checking time')
print('-I- RTCs current time: {}'.format(rtc.get_time_str()))
print('-I- Current NTP time: {}'.format(datetime.datetime.now()))

# update RTC if power was lost or if we have internet connection
print('-I- Checking to see if power was lost or if there is an internet connection')
if rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.set_datetime_now()
    print('-I- Power was lost, time updated to: {}'.format(rtc.get_time_str()))
elif rtc.get_power_lost() and not sys_mon.is_wlan_connected():
    print('-E- Power was lost and no internet connection, cannot update time!')
elif not rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.set_datetime_now()
    print('-I- There is an internet connection and power was not lost')
    print('-I- Time updated to: {}'.format(rtc.get_time_str()))
else:
    print('-I- Power was not lost and no connection to update time')


# while True:
# 	#
# 	currenttime = datetime.datetime.utcnow()
# 
# 	deltatime = currenttime - starttime
#  
# 	print ""
# 	print "Raspberry Pi=\t" + time.strftime("%Y-%m-%d %H:%M:%S")
# 	
# 	print "DS3231=\t\t%s" % ds3231.read_datetime()
# 
# 	print "DS3231 Temp=", ds3231.getTemp()
# 	time.sleep(1.0)
