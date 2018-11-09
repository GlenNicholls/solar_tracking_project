import sys
import time
import logging
import datetime
from Adafruit_MCP3008 import MCP3008
from test_utils import testUtils


# init logger
logger_name = 'main_logger'
test_handle = testUtils(logger_name)
logger = test_handle.init_logger()

# init ADC
CLK        = 21 # BCM pin numbering
MISO       = 19 # BCM pin numbering
MOSI       = 20 # BCM pin numbering
CS         = 10 # BCM pin numbering
NUM_ADC_CH = 8
adc = MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

logger.info('Monitoring ADC reads')


''' Test Routine
'''
def test_adc_read(num_checks=20):
    logger.info('----Raw ADC Reads----')
    string = []

    for adc_ch in range(NUM_ADC_CH):
        string.append('ADC Ch {}'.format(adc_ch))
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []

        for adc_ch in range(NUM_ADC_CH):
            raw_read = adc.read_adc(adc_ch)
            data.append(raw_read)
            assert raw_read > -1 and raw_read < 30 # if negative, BAD! if positive, should not read very high

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)

        time.sleep(0.25)
