import sys
import time
import logging
import datetime
import power_measurement import power_measurement
from Adafruit_MCP3008 import MCP3008
from test_utils import testUtils

# init logger
logger_name = 'main_logger'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
#testUtils(logger_name)

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


''' Helpers
'''
current_thresh = 0.01
voltage_thresh = 0.1
power_thresh  = current_thresh * voltage_thresh


def get_current(panel=False, battery=False):
    if not panel and not battery:
        raise ValueError('Must select power meas for battery or panel')

    A = None
    if panel:
        A = panel_power.get_current_A()
    elif battery:
        A =  battery_power.get_current_A()
    logger.INFO('Current: {} A'.format(A))
    return A


def get_voltage(panel=False, battery=False):
    if not panel and not battery:
        raise ValueError('Must select power meas for battery or panel')

    V = None
    if panel:
        V = panel_power.get_voltage_V()
    elif battery:
        V = battery_power.get_voltage_V()
    logger.INFO('Voltage: {} V'.format(V))
    return V

def get_power(panel=False, battery=False):
    if not panel and not battery:
        raise ValueError('Must select power meas for battery or panel')

    W = None
    if panel:
        W = panel_power.get_power_W()
    elif battery:
        W = battery_power.get_power_W()
    logger.INFO('Power: {} W'.format(W))
    return W



''' Test Routine
'''
def test_panel_current (num_checks = 20):
    for check in range(num_checks):
        A = get_current(panel=True)
        assert A < current_thresh # if reading larger than 10mA, no bueno
    
        time.sleep(0.25)

def test_panel_voltage (num_checks = 20):
    for check in range(num_checks):
        V = get_voltage(panel=True)
        assert V < voltage_thresh # if reading larger than 100mV, no bueno
    
        time.sleep(0.25)
        
def test_panel_power (num_checks = 20):
    for check in range(num_checks):
        W = get_power(panel=True)
        assert W < power_thresh # if reading larger than 1mW, no bueno
    
        time.sleep(0.25)

def test_battery_current (num_checks = 20):
    for check in range(num_checks):
        A = get_current(battery=True)
        assert A < current_thresh # if reading larger than 10mA, no bueno
    
        time.sleep(0.25)

def test_battery_voltage (num_checks = 20):
    for check in range(num_checks):
        V = get_voltage(battery=True)
        assert V < voltage_thresh # if reading larger than 100mV, no bueno
    
        time.sleep(0.25)
        
def test_battery_power (num_checks = 20):
    for check in range(num_checks):
        W = get_power(battery=True)
        assert W < power_thresh # if reading larger than 1mW, no bueno
    
        time.sleep(0.25)
