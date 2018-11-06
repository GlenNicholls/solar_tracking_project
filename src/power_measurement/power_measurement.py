from __future__ import division
from types import *
import time
import logging
import Adafruit_MCP3008


class power_measurement(object):
    
    def __init__(self, main_logger          = 'main_logger',
                       logger_module_name   = 'power_measurement',
                       adc_volt_ref         = 3.3,
                       adc_num_bits         = 10,
                       adc_current_channel  = 0,
                       adc_voltage_channel  = 0,
                       adc_object           = None,
                       current_amp_gain     = None,
                       current_amp_Rshunt   = None,
                       vdiv_R1              = None,
                       vdiv_R2              = None,
                 ):

        # instantiate logger
        self.logger = logging.getLogger(main_logger + '.' + logger_module_name)
        self.logger.info('creating an instance of the {}'.format(logger_module_name))

        # capture internal config
        self._v_ref        = adc_volt_ref
        self._adc_num_bits = adc_num_bits
        
        # ADC attributes
        self._adc_res = 2.0**adc_num_bits
        self._curr_ch = adc_current_channel
        self._volt_ch = adc_voltage_channel
        self._adc    = adc_object

        if len((self._curr_ch, self._volt_ch)) > len(set((self._curr_ch, self._volt_ch))): # appending tuples to check for uniqueness
            raise ValueError('ADC channels are not unique!')
        if type(self._curr_ch) != int or self._curr_ch < 0 or self._curr_ch > 7:
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        else:
            self.logger.debug('ADC current amplifier channel entered: {}'.format(self._curr_ch))
        if adc_object == None: # not sure how to check for class
            raise ValueError('No ADC object passed by reference!')

        # current amplifier attributes
        self._curr_G      = current_amp_gain
        self._curr_Rshunt = current_amp_Rshunt

        if type(self._curr_G) == None:
            raise ValueError('Invalid current amplifier gain, must be real!')
        else:
            self.logger.debug('Current amplifier gain: {}'.format(self._curr_G))
        if type(self._curr_Rshunt) == None:
            raise ValueError('Invalid current amplifier Rshunt, must be real value in [ohms]!')
        else:
            self.logger.debug('Current amplifier Rshunt: {}'.format(self._curr_Rshunt))

        # voltage divider attributes
        self._R1 = vdiv_R1
        self._R2 = vdiv_R2

        if self._R1 == None or self._R2 == None:
            raise ValueError('Invalid voltage divider resistance, must be real value in [ohms]!')
        else:
            self.logger.debug('Voltage divider R1: {} [ohm], Voltage divider R2: {} [ohm]'.format(self._R1, self._R2))
        


    def __read_adc_raw(self, adc_ch):
        raw_read = self._adc.read_adc(adc_ch)
        self.logger.debug('ADC raw read value: {}'.format(raw_read))
        return raw_read


    def __meas_adc_voltage(self, adc_ch):
        read_raw = self.__read_adc_raw(adc_ch)
        V = read_raw / self._adc_res
        self.logger.debug('ADC voltage conversion Vmeas: {} [V]'.format(V))
        return V

    
    # current measurement
    # current=(Vmeas/Gain)**2/R_shunt
    def get_current_A(self):
        Vmeas = self.__meas_adc_voltage(self._curr_ch)
        A = (Vmeas / self._curr_G) ** 2 / self._curr_Rshunt
        self.logger.debug('Measured current: {} [A]'.format(A))
        return A


    # voltage measurement
    # Vsrc = (R2+R1)/R2*Vmeas
    def get_voltage_V(self):
        Vmeas = self.__meas_adc_voltage(self._volt_ch)
        Vsrc = (self._R1 + self._R2) / self._R2 * Vmeas
        self.logger.debug('Measured voltage: {} [V]'.format(Vsrc))
        return Vsrc

    def get_power_W(self):
        V = self.get_voltage_V()
        A = self.get_current_A()
        W = V * A
        self.logger.debug('Measured power: {} [W]'.format(W))
        return W

    # TODO: run loop here or pass in list??
    #def get_energy_(self):
    
    # TODO: Add energy
    def get_all_measurements(self):
        A = self.get_current_A()
        V = self.get_voltage_V()
        W = self.get_power_W()
        return(A, V, W)
