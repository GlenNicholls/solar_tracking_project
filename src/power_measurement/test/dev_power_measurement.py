#!/usr/bin/python

from test_mcp3008 import *
from test_current_measurement import *
import time

# adc test
test_adc_read()

# power test
test_panel_current()
test_panel_voltage()
test_panel_power()

test_battery_current()
test_battery_voltage()
test_battery_power()

