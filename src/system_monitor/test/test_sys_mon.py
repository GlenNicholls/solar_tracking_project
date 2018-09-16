import time
import system_monitor


sys_mon = system_monitor.system_monitor()


print('-I- Monitoring system information')

str_p = []
str_p.append('temp [\'C]')
str_p.append('temp [\'F]')
str_p.append('temp [\'K]')
str_p.append('CPU [%]')
str_p.append('RAM [%]')
str_p.append('Disk [%]')

max_str_len = len( str(max(str_p, key=len)) )

str_format = ''
for i, str_enum in enumerate(str_p):
    str_format += '| {:^{buff_len}} '.format(str_enum, buff_len=max_str_len)
print(str_format + '|')

while True:
    # read data 
    data = []
    data.append(sys_mon.get_cpu_temp_C())
    data.append(sys_mon.get_cpu_temp_F())
    data.append(sys_mon.get_cpu_temp_K())
    data.append(sys_mon.get_cpu_use_perc())
    data.append(sys_mon.get_ram_use_perc())
    data.append(sys_mon.get_disk_use_perc())

    str_format = ''
    print( ('+' + '-' * (max_str_len + 2) ) * len(str_p) + '+')
    for i, data_enum in enumerate(data):
        str_format += '| {:{buff_len}.2f} '.format(data_enum, buff_len=max_str_len)
    print(str_format + '|')
    time.sleep(0.5)
