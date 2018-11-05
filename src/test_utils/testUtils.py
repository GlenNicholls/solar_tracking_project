import sys
import time
import logging
import datetime


class testUtils(object):
    def __init__ (self, logger_name = 'main_logger'):
        self._logger_name = logger_name

    def init_logger (self):
        # init logger
        main_logger = self._logger_name
        logger = logging.getLogger(main_logger)
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
            logger.error('You passed type: {}'.format(type(string)))
            raise ValueError('String is not of type list')

        if header:
            write_table_header(string, max_str_len)
        else:
            write_table_body(string, max_str_len)
