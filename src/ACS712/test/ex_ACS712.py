import time
import ACS712

# ACS712 configuration
ACS712_type     = 'ACS712_30AB'
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

# Other device configuration

print('-I- calibrating current sensor...')
current_sensor._calibrate()

print('Reading ACS712 value')
print('| {:^11} | {:^11} | {:^11} | {:^11} |'.format('current [A]', 'voltage [V]', 'power [W]', 'Raw ADC'))

while True:
    # read ADC channel 
    I = current_sensor.get_current_DC()
    V = current_sensor.get_voltage_DC()
    P = current_sensor.get_power_DC()
    adc_input = current_sensor._read_adc_raw()
    print('| {:11.5f} | {:11.5f} | {:11.5f} | {:11d} |'.format(I, V, P, adc_input))
    time.sleep(0.5)
