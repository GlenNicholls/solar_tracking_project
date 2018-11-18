from __future__ import division
import time
import logging

import motor_control.MotorCtrl_t as DIRECTION



class sun_sensor(object):

    def __init__ (self, logger_name         = 'main_logger',
                        logger_module_name  = 'sun_sensor',
                        mot_move_raw_thresh = None,
                        adc_volt_ref        = 3.3,
                        adc_north_sens_ch   = None,
                        adc_east_sens_ch    = None, 
                        adc_south_sens_ch   = None, 
                        adc_west_sens_ch    = None, 
                        adc_object          = None
                  ):

        # instantiate logger
        self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
        self.logger.info('creating an instance of the {}'.format(logger_module_name))

        # number of averages for measurements
        self._num_avgs = 20
        
        # logic thresh
        self._thresh = mot_move_raw_thresh
        if self._thresh == None or self._thresh <= 0 or self._thresh >= 1024:
            raise ValueError('Invalid threshold for motor movement, must be float [0-100]!')

        # capture internal config
        self._v_ref        = adc_volt_ref
        self._adc     = adc_object

        adc_ch_tuple = (adc_north_sens_ch, adc_east_sens_ch, adc_south_sens_ch, adc_west_sens_ch)
        if len(adc_ch_tuple) > len(set(adc_ch_tuple)): # appending tuples to check for uniqueness
            raise ValueError('ADC channels are not unique!')

        self._north = adc_north_sens_ch
        self._east = adc_east_sens_ch
        self._south = adc_south_sens_ch
        self._west = adc_west_sens_ch

        if self._north not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if self._east not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if self._south not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')
        if self._west not in range(8):
            raise ValueError('Invalid ADC channel, must be int 0-7!')

        if adc_object == None: # not sure how to check for class
            raise ValueError('No ADC object passed by reference!')



    def __read_adc(self, adc_ch):
        raw_read = self._adc.read_adc(adc_ch)
        self.logger.debug('ADC channel {} raw read value: {}'.format(adc_ch, raw_read))
        return raw_read


    def __get_diff(self, v_1, v_2):
        num_diff = v_1 - v_2
        den_diff = v_1 + v_2
        
        if den_diff == 0.0:
            diff = 0.0
            self.logger.warning('num 1 ({}) + num 2 ({}) returns zero!'.format(v_1, v_2))
            self.logger.warning('Divide by zero occuring. Returning zero')
        else:
            diff = num_diff/(den_diff / 2)
        self.logger.debug('Difference is: {}'.format(diff))
        return diff


    def eval_azimuth(self, avg_diff_azimuth):
        if abs(avg_diff_azimuth) > self._thresh:
            if avg_diff_azimuth > 0.0:
                self.logger.debug('Moving azimuth WEST')
                return DIRECTION.WEST
            else:
                self.logger.debug('Moving azimuth EAST')
                return DIRECTION.EAST
        else:
            self.logger.debug('Not greater than thresh, not updating azimuth')
            return DIRECTION.IDLE


    # TODO: use single eval function for both vertical/horizontal
    def eval_elevation(self, avg_diff_elevation):
        if abs(avg_diff_elevation) > self._thresh:
            if avg_diff_elevation > 0.0:
                self.logger.debug('Moving elevation SOUTH')
                return DIRECTION.SOUTH
            else:
                self.logger.debug('Moving elevation NORTH')
                return DIRECTION.NORTH 
        else:
            self.logger.debug('Not greater than thresh, not updating elevation')
            return DIRECTION.IDLE


    def get_diff_azimuth(self):
        east = self._read_adc(self._east)
        west = self._read_adc(self._west)
        diff = east - west
        #diff = self.__get_diff(east, west)
        self.logger.debug('Azimuth difference for east and west sensors: {}'.format(diff))
        return diff
    
    
    def get_diff_elevation(self):
        north = self._read_adc(self._north)
        south = self._read_adc(self._south)
        diff = north - south
        #diff  = self.__get_diff(north, south)
        self.logger.debug('Elevation difference for north and south sensors: {}'.format(diff))
        return diff
        
        
    def get_diff_all(self):
        azimuth   = self.get_diff_azimuth()
        elevation = self.get_diff_elevation()
        return azimuth, elevation
      

    def get_avg_azimuth(self):
        avg = 0
        azimuth = 0
        for i in range(self._num_avgs):
            azimuth += self.get_diff_azimuth()
        avg = azimuth/self._num_avgs
        self.logger.debug('Sun sensor azimuth average: {}'.format(avg))
        return avg
    
    
    def get_avg_elevation(self):
        avg = 0
        elevation = 0
        for i in range(self._num_avgs):
            elevation += self.get_diff_elevation()
        avg = elevation/self._num_avgs
        self.logger.debug('Sun sensor elevation average: {}'.format(avg))
        return avg
    
    
    def get_avg_all(self):
        azimuth   = self.get_avg_azimuth()
        elevation = self.get_avg_elevation()
        return (azimuth, elevation)
    
    
    def get_motor_direction_azimuth(self):
        az_avg = self.get_avg_azimuth()
        mot_dir = self.eval_azimuth(az_avg)
        return mot_dir
    
    
    def get_motor_direction_elevation(self):
        el_avg = self.get_avg_elevation()
        mot_dir = self.eval_elevation()
        return mot_dir
    
    
    def get_motor_direction_all(self):
        mot_dir_az = self.get_motor_direction_azimuth()
        mot_dir_el = self.get_motor_direction_elevation()
        return (mot_dir_az, mot_dir_el) 
