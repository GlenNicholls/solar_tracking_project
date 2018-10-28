import sys
import time
#from datetime import datetime
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


''' Functionality Helper Functions
'''
def configure_rtc():
    # Initial checks for time accuracy
    print('-I- Checking time')
    print('-I- RTCs current time: {}'.format(rtc.get_datetime_str()))
    print('-I- Current NTP time: {}'.format(datetime.datetime.now()))

    # update RTC if power was lost or if we have internet connection
    print('-I- Checking to see if power was lost or if there is an internet connection')
    if rtc.get_power_lost() and sys_mon.is_wlan_connected():
        rtc.set_datetime_now()
        print('-I- Power was lost, time updated to: {}'.format(rtc.get_datetime_str()))
    elif rtc.get_power_lost() and not sys_mon.is_wlan_connected():
        print('-E- Power was lost and no internet connection, cannot update time!')
    elif not rtc.get_power_lost() and sys_mon.is_wlan_connected():
        rtc.set_datetime_now()
        print('-I- There is an internet connection and power was not lost')
        print('-I- Time updated to: {}'.format(rtc.get_datetime_str()))
    else:
        print('-I- Power was not lost and no connection to update time')

    return rtc.get_datetime_delta()

def configure_rtc_alarm(alarm_in_x_secs):
    rtc.set_alarm_now_delta(seconds=alarm_in_x_secs)

def monitor_rtc_temp():
    temp = rtc.get_temp()
    return temp


''' Test Routine
'''
def test_configure_rtc():
    time_delta = configure_rtc()
    hours, minutes, seconds = str(time_delta).split(':')
    print('-I- Time difference between RTC and NTP: {}'.format(time_delta))

    assert not float(hours) and not float(minutes) and float(seconds) <= 2.0

def test_configure_rtc_alarm():
    print('-I- Testing alarm for RTC')
    test_fail = True
    secs_range = 5
    for alrm_in_x_secs in range(1, secs_range + 1):
        print('-I- Setting alarm for: {} s'.format(alrm_in_x_secs))

        configure_rtc_alarm(alrm_in_x_secs)      # configure alarm for x seconds from now
        time.sleep(alrm_in_x_secs + 1.5)               # give enough wait time for alarm
        alrm_flag = rtc.check_and_clear_alarms()     # if true, make sure we cleared alarm

        if alrm_flag:                                # we saw alarm which is good
            test_fail = rtc.check_and_clear_alarms() # did we clear alarm flags?
        else:
            test_fail = True
        assert not test_fail

def test_monitor_rtc_temp():
    print('-I- Testing RTC temperature')
    for i in range(10):
        temp = monitor_rtc_temp()
        print('-I- RTC temperature: {}'.format(temp))
        time.sleep(0.5)
        assert -40 < temp < 80
