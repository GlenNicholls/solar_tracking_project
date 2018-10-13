import time
import ACS712
from __future__ import division

# ACS712 configuration
ACS712_type     = 'ACS712_30AB'
bi_directional  = ACS712_type.lower().find('ab') > -1
Vref            = 3.3
num_adc_bits    = 10
hardware_spi_en = True
adc_channel     = 0
num_cal_avgs    = 20

current_sensor = ACS712.ACS712(device_type  = ACS712_type,
                               vref         = Vref,
                               num_adc_bits = num_adc_bits,
                               adc_channel  = adc_channel,
                               num_cal_avgs = num_cal_avgs,
                               hardware_spi = hardware_spi_en
                               )

if bi_directional: # set zero point based on sensor characteristics
    truth_zero = (2 ** num_adc_bits)/2
else:
    truth_zero = 0
adc_full_scale = 2**num_adc_bits


''' Helper Functions
'''
def calibrate_current_sensor():
    current_sensor.calibrate_current_sensor()
    return current_sensor._read_adc_raw()

def monitor_current_sensor():
    # read ADC channel 
    I       = current_sensor.get_current_DC()
    V       = current_sensor.get_voltage_DC()
    adc_raw = current_sensor._read_adc_raw()
    print('| {:11.5f} | {:11.5f} | {:11d} |'.format(I, V, P, adc_raw))
    return (I, V, adc_raw)

''' Test Routine
'''
def test_calibrate_current_sensor(accept_err_perc=1.0, num_checks=5):
    err_mult        = accept_err_perc/100

    for i in range(1, num_checks+1):
        print('-I- Check Calibration Iteration: {}'.format(i))
        raw_adc_val = calibrate_current_sensor()
        error = abs(truth_zero - raw_adc_val)
        print('-I- Sensor Error: {}'.format(error))
        assert error <= err_mult * 2**num_adc_bits

def test_monitor_current_sensor_readings(accept_err_perc=1.0, num_checks=20):
    err_mult = accept_err_perc/100

    print('-I- Reading Current Sensor Values:')
    print('| {:^11} | {:^11} | {:^11} | {:^11} |'.format('current [A]', 'voltage [V]', 'Raw ADC', 'Error'))
    # monitor loop
    for i in range(1, num_checks+1):
        I,V,adc_raw = monitor_current_sensor()
        error_raw = abs(truth_zero - adc_raw)
        print('| {:11.5f} | {:11.5f} | {:11d} | {:11d} |'.format(I, V, adc_raw, error_raw))
        assert error_raw <= (err_mult * adc_full_scale) 
        assert I <= 0.001
        assert V <= 0.001

test_calibrate_current_sensor()
test_monitor_current_sensor_readings()

# todo: after refactoring, add support for the below
# def test_calibrate_all_current_sensors()
# def test_calibrate_all_voltage_dividers()
# def test_calibrate_all_sun_sensors()
#
# def test_monitor_current_sensors()
# def test_monitor_voltage_dividers()
# def test_monitor_power_measurements()
# def test_monitor_all_sun_sensors
