#!/usr/bin/env python

import sys
import time
import logging
import datetime
from Adafruit_MCP3008 import MCP3008


# init logger
main_logger = 'main_logger'
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

# init ADC
CLK        = 40
MISO       = 35
MOSI       = 38
CS         = 19 
NUM_ADC_CH = 8
adc = MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

logger.info('Monitoring ADC reads')

''' Helper Functions
'''
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


''' Test Routine
'''
def test_adc_read(num_checks=20):
    logger.info('----Raw ADC Reads----')
    string = []

    for adc_ch in range(NUM_ADC_CH):
        string.append('ADC Ch {}'.format(adc_ch))
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []

        for adc_ch in range(NUM_ADC_CH):
            raw_read = adc.read_adc(adc_ch)
            data.append(raw_read)
            assert raw_read > -1 and raw_read < 30 # if negative, BAD! if positive, should not read very high

        write_table(string=data, max_str_len=max_str_len, header=False)

        time.sleep(0.25)
