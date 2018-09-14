import time
import ACS712

ACS712_type = 'ACS712_30A'
hardware_spi_en = True
num_adc_bits = 10
Vref = 3.3
current_sensor = ACS712(ACS712_type,
                        hardware_spi_en,
                        num_adc_bits,
                        Vref)

print('-I- calibrating current sensor...')
current_sensor._calibrate(adc_port=0, num_averages=10)

print('Reading ACS712 value')
print('| {0:>4} | {1:>4} | {2:>4} |'.format('current [I]', 'voltage [V]', 'power [W]'))

while True:
    # read ADC channel 
    I = current_sensor.get_current_DC()
    V = current_sensor.get_voltage_DC()
    P = current_sensor.get_power_DC()
    print('| {0:>4} | {1:>4} | {2:>4} |'.format(I, V, P))
    time.sleep(0.5)
