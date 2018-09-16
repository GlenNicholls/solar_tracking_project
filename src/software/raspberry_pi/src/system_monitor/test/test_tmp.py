import time
import system_monitor


temp_sensor = system_monitor.system_monitor()


print('-I- checking system temperature readings')

print('Reading ACS712 value')
print('| {:^5} | {:^5} | {:^5} |'.format('temp [\'C]', 'temp [\'F]', 'temp [\'K]'))

while True:
    # read ADC channel 
    temp_C = temp_sensor.get_cpu_temp_C()
    temp_F = temp_sensor.get_cpu_temp_F()
    temp_K = temp_sensor.get_cpu_temp_K()
    print('| {:5.2f} | {:5.2f} | {:5.2f} |'.format(temp_C, temp_F, temp_K))
    time.sleep(0.5)
