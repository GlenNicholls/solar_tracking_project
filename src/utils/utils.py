import os
import sys
import time
import logging
import datetime
import RPi.GPIO as GPIO
import pandas as pd
import pickle

class utils(object):
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
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
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



class hardware(object):
    def __init__(self, logger_name        = 'main_logger',
                       logger_module_name = 'hardware'
                ):
        self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
        self.logger.info('creating an instance of the ' + __name__ + ' with the alias {}'.format(logger_module_name))


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


class dataframe:
    '''
      create dataframe with given columnn names
      fromPickle: bool, if true make frame from pickle at fileLoc
      columns: array of column names
      fileLoc: string file location for dumps and restores
    '''
    def __init__(self, logger_name        = 'main_logger', 
                       logger_module_name = 'dataframe',
                       columns            = None,
                       file_name          = None, # NOTE: dont add .x
                       file_location      = None
                 ):
        self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
        self.logger.info('creating an instance of the ' + __name__ + ' with the alias {}'.format(logger_module_name))
        
        self._pd = pd
        
        # column names for dict
        self._columns = columns
        
        # file location
        self._file_name = file_name
        self._file_loc = file_location
        self._pickle_file = self._file_loc + self._file_name + '.pkl'
        self._csv_file = self._file_loc + self._file_name + '.csv'
        
        if os.path.isfile(self._pickle_file):
            self._frame = self._pd.read_pickle(self._pickle_file) 
        else:
            if self._columns == None:
                raise ValueError('Invalid column names, must be list of strings: [str1, str2,...]')
        
            self._frame = self._pd.DataFrame(columns=columns)
            self.logger.warning('Pickle file location does not exist! Creating file now: {}'.format(self._pickle_file))
            self._frame.to_pickle(self._pickle_file)


    '''
      return array of columns names
    '''
    def get_keys(self):
        column_names = self._frame.columns.values
        self.logger.debug('Column Names: {}'.format(column_names))
        return column_names
  
    
    '''
      push row data into df
      row: dict with keys that match frame column names
    '''
    def append_row(self, row):
        self._frame = self._frame.append(row, ignore_index=True)
        self.logger.debug('Appended row: {}'.format(row))
  
  
    '''
      pop row data into df
      row: dict with keys that match frame column names
    '''
    def get_row(self, row=1):
        tail = self._frame.tail(row)
        self.logger.info('Popped {} rows from the end: {}'.format(row, tail))
        return tail
      
    
    '''
      change fileLoc
    '''
    def set_file_location(self, new_loc):
        self.logger.debug('Changing pickle file location to: {}'.format(new_loc))
        self._file_loc = new_loc
        self._frame  = pd.read_pickle(self.fileLoc)
  
  
    '''
      dump frame to .pkl file at fileLoc location
    ''' 
    def dump_pickle(self):
        self.logger.info('Dumping dataframe to: {}'.format(self._pickle_file))
        self._frame.to_pickle(self._pickle_file)
        
        
    '''
      dump frame to .csv file at fileLoc location
    ''' 
    def dump_csv(self):
        self.logger.info('Dumping dataframe to: {}'.format(self._csv_file))
        self._frame.to_csv(self._csv_file, encoding='utf-8', index=False) #false index so we aren't writing index

