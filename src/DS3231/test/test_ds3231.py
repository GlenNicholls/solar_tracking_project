import sys
import time
import datetime
import DS3231



starttime = datetime.datetime.utcnow()

rtc = DS3231.DS3231(i2c_port=1, i2c_addr=0x68)
# uncomment next line if running on generation 1 pi:
#ds3231 = DS3231.DS3231(i2c_port=0, itc_addr=0x68)

# comment out the next line after the clock has been initialized
# ds3231.write_now()

print('-I- Monitoring DS3231 Information')

# Configure RTC
rtc.configure_ds3231()

# Initial checks for time accuracy
print('-I- Checking time as YYMMDDTHHMMSS')
print('-I- RTCs current time: {}'.format(rtc.read_str()))
print('-I- Current NTP time: {}'.format(datetime.datetime.utcnow()))

# update RTC if power was lost
print('-I- Checking to see if power was lost')
if rtc.get_power_lost():
    rtc.write_now()
    print('-I- Power was lost, time updated to: {}'.format())
else:
    print('-I- Power was not lost, starting log')


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
