#!/usr/bin/env python

from test_ds3231 import *
import time

alrm_in_x_secs = 3

test_configure_rtc()
configure_rtc_alarm(alrm_in_x_secs)

time.sleep(42)
clear_rtc_alarm()
