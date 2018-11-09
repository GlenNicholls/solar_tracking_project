import logging
import time
import system_monitor
from test_utils import testUtils

# init logger
logger_name = 'main_logger'
test_handle = testUtils(logger_name)
logger = test_handle.init_logger()


logger.info('Monitoring system information')
sys_mon = system_monitor.system_monitor(logger=logger_name)


def get_wifi_wlan():
    wifi_wlan    = sys_mon.is_wlan_connected()
    bit_rate     = sys_mon.get_wlan_bit_rate()
    link_quality = sys_mon.get_wlan_link_quality_perc()
    rx_pwr_dBm   = sys_mon.get_wlan_rx_pwr()

    return (bool(wifi_wlan), float(bit_rate.split(' ')[0]), link_quality, int(rx_pwr_dBm.split(' ')[0]))

def get_cpu_temp():
    temp_C = sys_mon.get_cpu_temp_C()
    temp_F = sys_mon.get_cpu_temp_F()
    temp_K = sys_mon.get_cpu_temp_K()
    return temp_C, temp_F, temp_K

def get_memory():
    cpu_use_perc  = sys_mon.get_cpu_use_perc()
    ram_use_perc  = sys_mon.get_ram_use_perc()
    disk_use_perc = sys_mon.get_disk_use_perc()
    return cpu_use_perc, ram_use_perc, disk_use_perc 


''' Test Routine
'''
def test_wifi_wlan(num_checks=20):
    logger.info('----WLAN Information----')
    string = []
    string.append('WiFi/WLAN Status')
    string.append('Bit Rate [Mbps]')
    string.append('Link Quality [%]')
    string.append('Rx Pwr [dBm]')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for i in range(num_checks):
        wifi_wlan, bit_rate, link_quality, rx_pwr_dBm = get_wifi_wlan()

        data = []
        data.append(wifi_wlan)
        data.append(bit_rate)
        data.append(link_quality)
        data.append(rx_pwr_dBm)

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)

        assert wifi_wlan
        assert bit_rate > 5
        assert link_quality > 2 # link quality needs to be better than 20 Mb/s
        assert rx_pwr_dBm > -70  # Rx power needs to be greater this dBm

        time.sleep(0.5)

def test_cpu_temp(num_checks=20):
    logger.info('----Temperature Information----')
    string = []
    string.append('Temp [\'C]')
    string.append('Temp [\'F]')
    string.append('Temp [\'K]')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for i in range(num_checks):
        temp_C, temp_F, temp_K = get_cpu_temp()

        data = []
        data.append(temp_C)
        data.append(temp_F)
        data.append(temp_K)

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)

        assert -40.0 < temp_C < 80.0 # tested operating range check

        time.sleep(0.5)

def test_memory(num_checks=20):
    logger.info('----Memory Information----')
    string = []
    string.append('CPU [%]')
    string.append('RAM [%]')
    string.append('DISK [%]')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for i in range(num_checks):
        cpu_use_perc, ram_use_perc, disk_use_perc = get_memory()

        data = []
        data.append(cpu_use_perc)
        data.append(ram_use_perc)
        data.append(disk_use_perc)

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)

        assert float(cpu_use_perc)  < 10.0 # tested CPU usage, too high for testing
        assert float(ram_use_perc)  < 30.0 # tested RAM usage, too high for testing
        assert float(disk_use_perc) < 80.0 # tested DISK usage, if >80%, could run into issues logging

        time.sleep(0.5)    
