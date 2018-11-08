from __future__ import division
import time
import logging


class sun_sensor(object):

    def __init__ (self, main_logger       = 'main_logger',
                       logger_module_name = 'sun_sensor',
                       move_motor_thresh_perc = None
                       adc_volt_ref   = 3.3,
                       adc_ur_sens_ch = None, # upper right sensor channel
                       adc_ul_sens_ch = None, # upper left sensor channel
                       adc_lr_sens_ch = None, # lower right sensor channel
                       adc_ll_sens_ch = None, # lower left sensor channel
                       adc_object     = None
                  ):

        # instantiate logger
        self.logger = logging.getLogger(main_logger + '.' + logger_module_name)
        self.logger.info('creating an instance of the {}'.format(logger_module_name))

        # logic thresh
        self._thresh_perc = move_motor_thresh_perc
        if self._thresh_perc == None or self._thresh_perc <= 0.0 or self._thresh_perc >= 100.0:
            raise ValueError('Invalid threshold for motor movement, must be float [0-100]!')

        # capture internal config
        self._v_ref        = adc_volt_ref

        self._adc_ch  = adc_channel
        self._adc     = adc_object

        adc_ch_tuple = (adc_ur_sens_ch, adc_ul_sens_ch, adc_lr_sens_ch, adc_ll_sens_ch)
        if len(adc_ch_tuple) > len(set(adc_ch_tuple)): # appending tuples to check for uniqueness
            raise ValueError('ADC channels are not unique!')

        self._ur = adc_ur_sens_ch
        self._ul = adc_ul_sens_ch
        self._lr = adc_lr_sens_ch
        self._ll = adc_ll_sens_ch

        if self._ur not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if self._ul not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if self._lr not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if self._ll not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')

        if adc_object == None: # not sure how to check for class
            raise ValueError('No ADC object passed by reference!')



    def __read_adc(self, adc_ch):
        raw_read = self._adc.read_adc(adc_ch)
        self.logger.debug('ADC raw read value: {}'.format(raw_read))
        return raw_read


    # def __meas_adc_voltage(self, adc_ch):
    #     read_raw = self.__read_adc_raw(adc_ch)
    #     V = read_raw / self._adc_res * self._v_ref
    #     self.logger.debug('ADC voltage conversion Vmeas: {} [V]'.format(V))
    #     return V


    def __get_per_diff(self, v_1, v_2):
        diff = (v_1-v_2)/((v_1+v_2)/2)
        self.logger.debug('Difference is: {}'.format(diff))
        return diff


    # TODO: use better noise reduction filter
    def __get_avg(self, diff_1, diff_2):
        avg = (diff_1 + diff_2)/2
        self.logger.debug('Average of difference: {}'.format(avg))
        return avg


    def eval_horizontal(self, avg_diff_horizon):
        if abs(avg_diff_horizon) > self._thresh_perc:
            if avg_diff_horizon < 0.0:
                self.logger.debug('Moving horizon left')
                return 1 # move left
            else:
                self.logger.debug('Moving horizon right')
                return -1 # move right
        else:
            self.logger.debug('Not greater than thresh, not updating horizon')
            return 0


    # TODO: use single eval function for both vertical/horizontal
    def eval_vertical(self, avg_diff_vertical):
        if abs(avg_diff_vertical) > self._thresh_perc:
            if avg_diff_vertical < 0.0:
                self.logger.debug('Moving vertical up')
                return -1 # move left
            else:
                self.logger.debug('Moving vertical down')
                return 1 # move right
        else:
            self.logger.debug('Not greater than thresh, not updating vertical')
            return 0


    def get_diff_upper_perc(self):
        diff = self.__get_per_diff(self.__read_adc(self._ul), self.__read_adc(self._ur))
        self.logger.debug('Sun sensor percent difference for upper left and upper right: {}'.format(diff))
        return diff


    def get_diff_lower_perc(self):
        diff = self.__get_per_diff(self.__read_adc(self._ll), self.__read_adc(self._lr))
        self.logger.debug('Sun sensor percent difference for lower left and lower right: {}'.format(diff))
        return diff


    def get_diff_left_perc(self):
        diff = self.__get_per_diff(self.__read_adc(self._ul), self.__read_adc(self._ll))
        self.logger.debug('Sun sensor percent difference for upper left and lower left: {}'.format(diff))
        return diff


    def get_diff_right_perc(self):
        diff = self.__get_per_diff(self.__read_adc(self._ur), self.__read_adc(self._lr))
        self.logger.debug('Sun sensor percent difference for upper right and lower right: {}'.format(diff))
        return diff


    def get_all_diff_perc(self):
        upper = self.get_diff_upper_perc()
        lower = self.get_diff_lower_perc()
        left  = self.get_diff_left_perc()
        right = self.get_diff_right_perc()
        return (upper, lower, left, right)


    # TODO: change all horizon/vertical to azimuth/elevation to make clear
    def get_avg_horizon(self):
        upper, lower, _, _ = self.get_all_diff_perc()
        avg = self.__get_avg(upper, lower)
        self.logger.debug('Sun sensor horizon average: {}'.format(avg))
        return avg

    def get_avg_vertical(self):
        _, _, left, right = self.get_all_diff_perc()
        avg = self.__get_avg(left, right)
        self.logger.debug('Sun sensor vertical average: {}'.format(avg))
        return avg


    def get_all_avg(self):
        horizon  = self.get_avg_horizon()
        vertical = self.get_avg_vertical()
        return (horizon, vertical)


    # TODO: make better name
    def move_motor(self):
        horizon, vertical = self.get_all_avg()
        move_horiz_mot = self.eval_horizontal(horizon)
        move_vert_mot = self.eval_horizontal(vertical)
        return (move_horiz_mot, move_vert_mot)

