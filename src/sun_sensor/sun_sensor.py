from __future__ import division
import time
import logging


class sun_sensor(object):

    def __init__ (self, main_logger       = 'main_logger',
                       logger_module_name = 'sun_sensor',
                       adc_volt_ref       = 3.3,
                       adc_num_bits       = 10,
                       adc_nw_sens_ch     = None,# north west
                       adc_ne_sens_ch     = None,# north east
                       adc_sw_sens_ch     = None,# south west
                       adc_se_sens_ch     = None,# south east
                       adc_object         = None
                  ):

        # instantiate logger
        self.logger = logging.getLogger(main_logger + '.' + logger_module_name)
        self.logger.info('creating an instance of the {}'.format(logger_module_name))

        # capture internal config
        self._v_ref        = adc_volt_ref
        self._adc_num_bits = adc_num_bits

        self._adc_res = 2.0**adc_num_bits
        self._adc_ch  = adc_channel
        self._adc     = adc_object

        adc_ch_tuple = (adc_nw_sens_ch, adc_ne_sens_ch, adc_sw_sens_ch, adc_se_sens_ch)
        if len(adc_ch_tuple) > len(set(adc_ch_tuple)): # appending tuples to check for uniqueness
            raise ValueError('ADC channels are not unique!')

        if adc_nw_sens_ch not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if adc_ne_sens_ch not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if adc_sw_sens_ch not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if adc_se_sens_ch not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')

        if adc_object == None: # not sure how to check for class
            raise ValueError('No ADC object passed by reference!')



    def __read_adc_raw(self, adc_ch):
        raw_read = self._adc.read_adc(adc_ch)
        self.logger.debug('ADC raw read value: {}'.format(raw_read))
        return raw_read


    def __meas_adc_voltage(self, adc_ch):
        read_raw = self.__read_adc_raw(adc_ch)
        V = read_raw / self._adc_res * self._v_ref
        self.logger.debug('ADC voltage conversion Vmeas: {} [V]'.format(V))
        return V


    def __get_per_diff(self, v_1, v_2):
        diff = (v_1-v_2)/((v_1+v_2)/2)
        self.logger.debug('Difference is: {}'.format(diff))
        return diff


    def __get_avg(self, diff_1, diff_2):
        avg = (diff_1 + diff_2)/2
        self.logger.debug('Average of difference: {}'.format(avg))
        return avg


    def eval_horizontal(self, avg_diff_horizon):
        if abs(avg_diff_horizon) > per_diff_threshold:
            if avg_diff_horizon < 0.0:
                self.logger.debug('Moving horizon left')
                return 1 # move left
            else:
                self.logger.debug('Moving horizon right')
                return -1 # move right
        else:
            self.logger.debug('Not greater than thresh, not updating horizon')
            return 0


    def eval_vertical(self, avg_diff_vertical):
        if abs(avg_diff_vertical) > per_diff_threshold:
            if avg_diff_vertical < 0.0:
                self.logger.debug('Moving vertical up')
                return -1 # move left
            else:
                self.logger.debug('Moving vertical down')
                return -1 # move right
        else:
            self.logger.debug('Not greater than thresh, not updating vertical')
            return 0
