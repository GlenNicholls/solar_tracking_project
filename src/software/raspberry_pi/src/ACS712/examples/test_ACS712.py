import time
import ACS712

# ACS712 configuration
ACS712_type     = 'ACS712_30A'
Vref            = 3.3
num_adc_bits    = 10
hardware_spi_en = True
adc_port        = 0
num_cal_avgs    = 20

current_sensor = ACS712.ACS712(device_type  = ACS712_type,
                               vref         = Vref,
                               num_adc_bits = num_adc_bits,
                               adc_port     = adc_port,
                               num_cal_avgs = num_cal_avgs,
                               hardware_spi = hardware_spi_en
                               )

# Other device configuration

print('-I- calibrating current sensor...')
current_sensor._calibrate()

print('Reading ACS712 value')
print('| {0:>4} | {1:>4} | {2:>4} |'.format('current [I]', 'voltage [V]', 'power [W]'))

while True:
    # read ADC channel 
    I = current_sensor.get_current_DC()
    V = current_sensor.get_voltage_DC()
    P = current_sensor.get_power_DC()
    print('| {0:>4} | {1:>4} | {2:>4} |'.format(I, V, P))
    time.sleep(0.5)
