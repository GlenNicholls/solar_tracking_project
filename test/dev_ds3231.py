#!/usr/bin/python

from test_ds3231 import *
import time

alrm_in_x_secs = 3

test_configure_rtc()
configure_rtc_alarm(alrm_in_x_secs)

time.sleep(alrm_in_x_secs + 10)
clear_rtc_alarm()
