import sys
import time
import datetime
import DS3231
import system_monitor


starttime = datetime.datetime.utcnow()

# create RTC object
rtc = DS3231.DS3231(i2c_port=1, i2c_addr=0x68)
# uncomment next line if running on generation 1 pi:
#ds3231 = DS3231.DS3231(i2c_port=0, itc_addr=0x68)

# create system monitor object
sys_mon = system_monitor.system_monitor()

# comment out the next line after the clock has been initialized
# ds3231.write_now()

print('-I- Monitoring DS3231 Information')

# Configure RTC
rtc.configure_ds3231()

# Initial checks for time accuracy
print('-I- Checking time as YYMMDDTHHMMSS')
print('-I- RTCs current time: {}'.format(rtc.read_str()))
print('-I- Current NTP time: {}'.format(datetime.datetime.utcnow()))

# update RTC if power was lost or if we have internec connection
print('-I- Checking to see if power was lost or if there is an internet connection')
if rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.write_now()
    print('-I- Power was lost, time updated to: {}'.format(rtc.read_str()))
elif rtc.get_power_lost() and not sys_mon.is_wlan_connected():
    print('-E- Power was lost and no internet connection, cannot update time!')
elif not rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.write_now()
    print('-I- There is an internet connection and power was not lost')
    print('-I- Time updated to: {}'.format(rtc.read_str()))
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
