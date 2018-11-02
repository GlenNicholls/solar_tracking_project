#!/usr/bin/env python

import sys
import time
import datetime
import DS3231
import system_monitor

main_logger = 'main_logger'
logger = logging.getLogger(main_logger)
logger.setLevel(logging.INFO)
# create console handler to log to the terminal
ch = logging.StreamHandler()
# set logging level to debug, will switch to info for final version
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)


# create RTC object
i2c_port  = 1 # set to 0 if using gen 1 pi
i2c_addr  = 0x68
latitude  = 39.7392
longitude = 104.9903
rtc = DS3231.DS3231(logger    = main_logger,
                    i2c_port  = i2c_port,
                    i2c_addr  = i2c_addr,
                    latitude  = latitude,
                    longitude = longitude)

# create system monitor object
sys_mon = system_monitor.system_monitor(logger = main_logger)

logger.info('Monitoring DS3231 Information')

# Configure RTC
rtc.configure_rtc()


''' Functionality Helper Functions
'''
def configure_rtc():
    # Initial checks for time accuracy
    logger.info('Checking time')
    logger.info('RTCs current time: {}'.format(rtc.get_datetime_str()))
    logger.info('Current NTP time: {}'.format(datetime.datetime.now()))

    # update RTC if power was lost or if we have internet connection
    logger.info('Checking to see if power was lost or if there is an internet connection')
    if rtc.get_power_lost() and sys_mon.is_wlan_connected():
        rtc.set_datetime_now()
        logger.info('Power was lost, time updated to: {}'.format(rtc.get_datetime_str()))
    elif rtc.get_power_lost() and not sys_mon.is_wlan_connected():
        logger.error('Power was lost and no internet connection, cannot update time!')
    elif not rtc.get_power_lost() and sys_mon.is_wlan_connected():
        rtc.set_datetime_now()
        logger.info('There is an internet connection and power was not lost')
        logger.info('Time updated to: {}'.format(rtc.get_datetime_str()))
    else:
        logger.info('Power was not lost and no connection to update time')

    return rtc.get_datetime_delta()

def configure_rtc_alarm(alarm_in_x_secs):
    rtc.set_alarm_now_delta(seconds=alarm_in_x_secs)

def clear_rtc_alarm():
    rtc.check_and_clear_alarms()

def monitor_rtc_temp():
    temp = rtc.get_temp()
    return temp


''' Test Routine
'''
def test_configure_rtc():
    time_delta = configure_rtc()
    hours, minutes, seconds = str(time_delta).split(':')
    logger.info('Time difference between RTC and NTP: {}'.format(time_delta))

    assert not float(hours) and not float(minutes) and float(seconds) <= 2.0

def test_configure_rtc_alarm():
    logger.info('Testing alarm for RTC')
    test_fail = True
    secs_range = 5
    for alrm_in_x_secs in range(1, secs_range + 1):
        logger.info('Setting alarm for: {} s'.format(alrm_in_x_secs))

        configure_rtc_alarm(alrm_in_x_secs)      # configure alarm for x seconds from now
        time.sleep(alrm_in_x_secs + 1.5)               # give enough wait time for alarm
        alrm_flag = rtc.check_and_clear_alarms()     # if true, make sure we cleared alarm

        if alrm_flag:                                # we saw alarm which is good
            test_fail = rtc.check_and_clear_alarms() # did we clear alarm flags?
        else:
            test_fail = True
        assert not test_fail

def test_monitor_rtc_temp():
    logger.info('Testing RTC temperature')
    for i in range(10):
        temp = monitor_rtc_temp()
        logger.info('RTC temperature: {}'.format(temp))
        time.sleep(0.5)
        assert -40 < temp < 80
