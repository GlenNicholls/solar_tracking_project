import os
import time


# REFERENCE: https://www.raspberrypi.org/forums/viewtopic.php?t=22180

class system_monitor(object):
    ''' Note: if these are called all at same time, they will yield different answers as 
              they are sampled at different times. Not by much, but enough to make readings
              look incorrect. Can fix by always calling get_cpu_temp_C and using this value
              globally in the without calling this function for the other readings.
    '''
    def __init__(self):
        self._temp_C   = 0.0
        self._temp_F   = 0.0
        self._temp_K   = 0.0
        self._cpu_use  = 0.0
        self._ram_use  = 0.0
        self._disk_use = 0.0

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

