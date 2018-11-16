import sys
import time
import logging
import datetime


class utils:
    def __init__ (self, logger_name = 'main_logger', debug=False):
        self._logger_name = logger_name
        self._dbg = debug
    
    def init_logger (self):
        # init logger
        main_logger = self._logger_name
        logger = logging.getLogger(main_logger)
        
        if self._dbg:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        # create console handler to log to the terminal
        ch = logging.StreamHandler()
        # set logging level to debug, will switch to info for final version
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # add the handlers to logger
        logger.addHandler(ch)

        return logger

    def set_module_log_level_dbg(self, logger_module_name, logger_name):
        logging.getLogger(logger_name + '.' + logger_module_name).setLevel(logging.DEBUG)
    
    
    def set_module_log_level_info(self, logger_module_name, logger_name):
        logging.getLogger(logger_name + '.' + logger_module_name).setLevel(logging.INFO)


    def __write_table_header(self, string=[], max_str_len=None):
        str_to_write = ''
        for i, str_enum in enumerate(string):
            str_to_write += '| {:^{buff_len}} '.format(str_enum, buff_len=max_str_len)
        print(str_to_write + '|')


    def __write_table_body(self, string=[], max_str_len=None):
        str_to_write = ''
        num_cols = len(string)
        print( ('+' + '-' * (max_str_len + 2) ) * num_cols + '+')
        for i, str_enum in enumerate(string):
            str_to_write += '| {:^{buff_len}} '.format(str_enum, buff_len=max_str_len)
        print(str_to_write + '|')


    # TODO: scale float precision to max size - some fixed amount
    def write_table(self, string=[], max_str_len=None, header=False):
        if max_str_len == None or type(max_str_len) != int or max_str_len <= 1:
            raise ValueError('Max string length must be integer >= 1')
        if type(string) != list:
            logger.error('You passed type: {}'.format(type(string)))
            raise ValueError('String is not of type list')

        if header:
            self.__write_table_header(string, max_str_len)
        else:
            self.__write_table_body(string, max_str_len)



import RPi.GPIO as GPIO  

class hardware:
    def __init__(self, logger_name        = 'main_logger',
                       logger_module_name = 'hardware'
                ):
        self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
        self.logger.info('creating an instance of the {}'.format(logger_module_name))


    def pin_is_set(self, pin):
        pin_state = GPIO.input(pin)
        self.logger.debug('Pin {} state: {}'.format(pin, pin_state))
        return pin_state

    
    def set_pin_high(self, pin):
        self.logger.debug('Setting pin {} HIGH'.format(pin))
        GPIO.output(pin, GPIO.HIGH)


    def set_pin_low(self, pin):
        self.logger.debug('Setting pin {} LOW'.format(pin))
        GPIO.output(pin, GPIO.LOW)

