import time
import system_monitor


print('-I- Monitoring system information')
sys_mon = system_monitor.system_monitor()


''' Helper Functions
'''
def write_table_header(string=[], max_str_len=None):
    str_to_write = ''
    for i, str_enum in enumerate(string):
        str_to_write += '| {:^{buff_len}} '.format(str_enum, buff_len=max_str_len)
    print(str_to_write + '|')

def write_table_body(string=[], max_str_len=None):
    str_to_write = ''
    num_cols = len(string)
    print( ('+' + '-' * (max_str_len + 2) ) * num_cols + '+')
    for i, str_enum in enumerate(string):
        str_to_write += '| {:^{buff_len}} '.format(str_enum, buff_len=max_str_len)
    print(str_to_write + '|')

def write_table(string=[], max_str_len=None, header=False):
    if max_str_len == None or type(max_str_len) != int or max_str_len <= 1:
        raise ValueError('Max string length must be integer >= 1')
    if type(string) != list:
        print('-E- You passed type: {}'.format(type(string)))
        raise ValueError('String is not of type list')

    if header:
        write_table_header(string, max_str_len)
    else:
        write_table_body(string, max_str_len)


def check_wifi_wlan():
    wifi_wlan    = sys_mon.is_wlan_connected()
    bit_rate     = sys_mon.get_wlan_bit_rate()
    link_quality = sys_mon.get_wlan_link_quality_perc()
    rx_pwr_dBm   = sys_mon.get_wlan_rx_pwr()

    return (bool(wifi_wlan), float(bit_rate.split(' ')[0]), link_quality, int(rx_pwr_dBm.split(' ')[0]))

''' Test Routine
'''
def test_check_wifi_wlan(num_checks=20):
    print('-I- ----WLAN Information----')
    string = []
    string.append('WiFi/WLAN Status')
    string.append('Bit Rate [Mbps]')
    string.append('Link Quality [%]')
    string.append('Rx Pwr [dBm]')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    write_table(string=string, max_str_len=max_str_len, header=True)

    for i in range(num_checks):
        wifi_wlan, bit_rate, link_quality, rx_pwr_dBm = check_wifi_wlan()

        data = []
        data.append(wifi_wlan)
        data.append(bit_rate)
        data.append(link_quality)
        data.append(rx_pwr_dBm)

        write_table(string=data, max_str_len=max_str_len, header=False)

        assert wifi_wlan
        assert bit_rate > 5
        assert link_quality > 45 # link quality needs to be better than 25%
        assert rx_pwr_dBm > -65    # Rx power needs to be greater than -50 dBm

        time.sleep(0.5)

    
test_check_wifi_wlan()
# while True:
#     # read data 
#     data = []
#     data.append(sys_mon.get_cpu_temp_C())
#     data.append(sys_mon.get_cpu_temp_F())
#     data.append(sys_mon.get_cpu_temp_K())
#     data.append(sys_mon.get_cpu_use_perc())
#     data.append(sys_mon.get_ram_use_perc())
#     data.append(sys_mon.get_disk_use_perc())
# 
#     sys_mon._get_connection_info()
# 
#     str_format = ''
#     print( ('+' + '-' * (max_str_len + 2) ) * len(str_p) + '+')
#     for i, data_enum in enumerate(data):
#         str_format += '| {:{buff_len}.2f} '.format(data_enum, buff_len=max_str_len)
#     print(str_format + '|')
#     time.sleep(0.5)
