import sys
import time
import logging
import datetime
import power_measurement import power_measurement
from Adafruit_MCP3008 import MCP3008
from test_utils import testUtils

# init logger
logger_name = 'main_logger'
testUtils(logger_name)

# init ADC
CLK        = 21 # BCM pin numbering
MISO       = 19 # BCM pin numbering
MOSI       = 20 # BCM pin numbering
CS         = 10 # BCM pin numbering
NUM_ADC_CH = 8
adc = MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# init power measurement
adc_vref     = 3.3
adc_num_bits = 10

adc_panel_curr_ch        = 0
adc_panel_volt_ch        = 3
curr_sensor_panel_G      = 75
curr_sensor_panel_Rshunt = 0.3
vdiv_panel_R1            = 1000
vdiv_panel_R2            = 160

adc_battery_curr_ch        = 1
adc_battery_volt_ch        = 2
curr_sensor_battery_G      = 75
curr_sensor_battery_Rshunt = 0.001
vdiv_battery_R1            = 1000
vdiv_battery_R2            = 360

panel_power = ( main_logger          = logger_name
                logger_module_name   = 'panel_power',
                adc_volt_ref         = adc_vref,
                adc_num_bits         = adc_num_bits,
                adc_current_channel  = adc_panel_curr_ch,
                adc_voltage_channel  = adc_panel_volt_ch,
                adc_object           = adc,
                current_amp_gain     = curr_sensor_panel_G,
                current_amp_Rshunt   = curr_sensor_panel_Rshunt,
                vdiv_R1              = vdiv_panel_R1,
                vdiv_R2              = vdiv_panel_R2
               )

battery_power = ( main_logger          = logger_name
                  logger_module_name   = 'battery_power',
                  adc_volt_ref         = adc_vref,
                  adc_num_bits         = adc_num_bits,
                  adc_current_channel  = adc_battery_curr_ch,
                  adc_voltage_channel  = adc_battery_volt_ch,
                  adc_object           = adc,
                  current_amp_gain     = curr_sensor_battery_G,
                  current_amp_Rshunt   = curr_sensor_battery_Rshunt,
                  vdiv_R1              = vdiv_battery_R1,
                  vdiv_R2              = vdiv_battery_R2
                 )
logger.info('Monitoring power measurements')

