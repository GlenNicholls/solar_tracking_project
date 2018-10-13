from __future__ import division 
import time
import os
import re
import shlex
from subprocess import Popen, PIPE, check_call


# REFERENCE: https://www.raspberrypi.org/forums/viewtopic.php?t=22180

class system_monitor(object):
    ''' Note: if these are called all at same time, they will yield different answers as 
              they are sampled at different times. Not by much, but enough to make readings
              look incorrect. Can fix by always calling get_cpu_temp_C and using this value
              globally in the without calling this function for the other readings.
    '''
    def __init__(self, wlan_interface='wlan0'):
        self._wlan_interface = wlan_interface.lower()
        self._wlan_out = []
        self._temp_C   = 0.0
        self._temp_F   = 0.0
        self._temp_K   = 0.0
        self._cpu_use  = 0.0
        self._ram_use  = 0.0
        self._disk_use = 0.0


    ''' Temperature Information
    '''
    # get current cpu temp in 'C
    def get_cpu_temp_C(self):
        res = os.popen('vcgencmd measure_temp').readline()
        self._temp_C = float( res.replace("temp=","").replace("'C\n","") )
        return self._temp_C

    # get current cpu temp in 'F
    def get_cpu_temp_F(self):
        self._temp_F = self.get_cpu_temp_C() * 9.0/5.0 + 32.0
        return self._temp_F

    # get current cpu temp in K... just because
    def get_cpu_temp_K(self):
        self._temp_K = self.get_cpu_temp_C() + 273.15
        return self._temp_K

    # get current cpu usage in %
    def get_cpu_use_perc(self):
        self._cpu_use = float( os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip('\\') )
        return self._cpu_use


    ''' RAM and Disk Information
    '''
    # Get RAM information
    # Index 0: total RAM in Mb                                                                
    # Index 1: used RAM in Mb                                                          
    # Index 2: free RAM in Mb
    def get_ram_info(self):
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                return map( float, line.split()[1:4] ) # map all strings to ints

    # get ram usage in %
    def get_ram_use_perc(self):
        self._ram_use = self.get_ram_info()[1] / self.get_ram_info()[0] * 100  
        return self._ram_use

    # get disk information                     
    # Index 0: total disk space in G                                                        
    # Index 1: used disk space in G                                                    
    # Index 2: remaining disk space in G                                                     
    # Index 3: percentage of disk used %                                                
    def get_disk_info(self):
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i +1
            line = p.readline()
            if i==2:
                return line.split()[1:5]

    # get disk usage in %
    def get_disk_use_perc(self):
        self._disk_use = float(self.get_disk_info()[3].strip('%'))
        return self._disk_use


    ''' WIFI/WLAN Connection Information
    '''
    # get connection info
    # ex ouput:
    # wlan0     IEEE 802.11  ESSID:"RCMP Surveillance Horse 4"
    #           Mode:Managed  Frequency:2.427 GHz  Access Point: 70:4D:7B:DF:69:18
    #           Bit Rate=72.2 Mb/s   Tx-Power=31 dBm
    #           Retry short limit:7   RTS thr:off   Fragment thr:off
    #           Power Management:on
    #           Link Quality=59/70  Signal level=-51 dBm
    #           Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
    #           Tx excessive retries:0  Invalid misc:0   Missed beacon:0
    def _get_connection_info(self):
        cmd = Popen('iwconfig {}'.format(self._wlan_interface),
                                shell=True, stdout=PIPE)
        self._wlan_out = cmd.communicate()[0].replace(' '*10,'')
        self._wlan_out = re.split('\n|   |  ', self._wlan_out)

    # is WLAN connected?
    # todo: test this function locally
    def is_wlan_connected(self):
        self._get_connection_info()
        for i, line in enumerate(self._wlan_out):
            if line.find('Not-Associated') > -1 or line.find('No such device') > -1:
                connected =  False
                break
            else:
                connected =  True
        return connected

    # get data rate
    def get_wlan_bit_rate(self):
        self._get_connection_info()
        for i, line in enumerate(self._wlan_out):
            if line.find('Bit Rate') > -1:
                bit_rate = line.split('=')[1]
                break
            else:
                bit_rate = None
        return bit_rate

    # get data rate in Mb/s
    def get_wlan_link_quality_perc(self):
        self._get_connection_info()
        for i, line in enumerate(self._wlan_out):
            if line.find('Link Quality') > -1:
                tmp = float(re.split('=|/', line)[1]) / float(re.split('=|/', line)[2])
                link_quality = '{:.2f}'.format(float(tmp) * 100.0 )
                break
            else:
                link_quality = None
        return link_quality

    def get_wlan_rx_pwr(self):
        self._get_connection_info()
        for i, line in enumerate(self._wlan_out):
            if line.find('Signal level') > -1:
                rx_power = line.split('=')[1]
                break
            else:
                rx_power = None
        return rx_power

    # get wifi name
    def get_wlan_wifi_name(self):
        self._get_connection_info()
        for i, line in enumerate(self._wlan_out):
            if line.find('ESSID') > -1:
                name = line.split(':')[1]
                break
            else:
                name = None
        return name
