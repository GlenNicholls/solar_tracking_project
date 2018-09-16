import os
import time


class system_monitor(object):

    def __init__(self):
        self._temp_C = 0.0
        self._temp_F = 0.0
        self._temp_K = 0.0


    def get_cpu_temp_C(self):
        res = os.popen('vcgencmd measure_temp').readline()
        self._temp_C = res.replace("temp=","").replace("'C\n","")
        print(res)
        print(res.replace("temp=",""))
        print(replace("'C\n",""))
        return(res.replace("temp=","").replace("'C\n",""))


    def get_cpu_temp_F(self):
        self._temp_F = get_cpu_temp_C() * 9.0/5.0 + 32
        return self._temp_F


    def get_cpu_temp_K(self):
        self._temp_K = get_cpu_temp_C() + 273.15
        return self._temp_K


