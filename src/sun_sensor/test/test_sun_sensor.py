import sys
import time
import logging
import datetime
from sun_sensor import sun_sensor
from Adafruit_MCP3008 import MCP3008
from test_utils import testUtils


# init logger
logger_name = 'main_logger'
logger = logging.getLogger(logger_name)
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
CLK        = 21 # BCM pin numbering
MISO       = 19 # BCM pin numbering
MOSI       = 20 # BCM pin numbering
CS         = 10 # BCM pin numbering
NUM_ADC_CH = 8
adc = MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# init sun sensor
adc_vref     = 3.3

move_thresh_perc = 0.1
up_right_sens_ch = 4 # can change since connections come in on header
up_left_sens_ch  = 5 # can change since connections come in on header
lo_right_sens_ch = 6 # can change since connections come in on header
lo_left_sens_ch  = 7 # can change since connections come in on header
adc_channels = [up_right_sens_ch, up_left_sens_ch, lo_right_sens_ch, lo_left_sens_ch]

sun_sensor( main_logger        = logger_name,
            logger_module_name = 'sun_sensor',
            move_motor_thresh_perc = move_thresh_perc
            adc_volt_ref   = adc_vref,
            adc_ur_sens_ch = up_right_sens_ch, # upper right sensor channel
            adc_ul_sens_ch = up_left_sens_ch,  # upper left sensor channel
            adc_lr_sens_ch = lo_right_sens_ch, # lower right sensor channel
            adc_ll_sens_ch = lo_left_sens_ch,  # lower left sensor channel
            adc_object     = adc
           )


''' Test Routine
'''
def test_sens_channels(num_checks=20):
    string = []

    for _,adc_ch in enumerate(adc_channels):
        string.append('ADC Ch {}'.format(adc_ch))
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    testUtils.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []

        for adc_ch in enumerate(adc_channels):
            raw_read = adc.read_adc(adc_ch)
            data.append(raw_read)
            assert raw_read > -1 and raw_read < 30 # if negative, BAD! if positive, should not read very high

        testUtils.write_table(string=data, max_str_len=max_str_len, header=False)
        time.sleep(0.15)


def test_sun_sensor_differences(num_checks=20):
    string = []

    string.append('Upper [%]')
    string.append('Lower [%]')
    string.append('Left [%]')
    string.append('Right [%]')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    testUtils.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []
        upper, lower, left, right = sun_sensor.get_all_diff_perc()
        data.append(upper)
        data.append(lower)
        data.append(left)
        data.append(right)

        testUtils.write_table(string=data, max_str_len=max_str_len, header=False)

        # TODO: add parameter threshold
        assert upper < 1.0 # unconnected should yield next to zero difference
        assert lower < 1.0 # unconnected should yield next to zero difference
        assert left  < 1.0 # unconnected should yield next to zero difference
        assert right < 1.0 # unconnected should yield next to zero difference

        time.sleep(0.15)


def test_sun_sensor_averages(num_checks=20):
    string = []

    string.append('Avg Horizon [%]')
    string.append('Avg Vertical [%]')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    testUtils.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []
        horizon, vertical = sun_sensor.get_all_avg()
        data.append(horizon)
        data.append(vertical)

        testUtils.write_table(string=data, max_str_len=max_str_len, header=False)

        # TODO: add parameter threshold
        assert horizon  < 0.5 # unconnected should yield next to zero difference
        assert vertical < 0.5 # unconnected should yield next to zero difference

        time.sleep(0.15)


def test_motor_move_flags(num_checks=20):
    for check_num in range(num_checks):
        horizon, vertical = sun_sensor.get_all_avg()
        horiz_mov, vert_mov = sun_sensor.move_motor()

        if abs(horizon) > move_thresh_perc:
            assert horiz_mov != 0 # motor flag should be -1 or 1
        else:
            assert horiz_mov == 0 # motor flag should not be set
        if abs(vertical) > move_thresh_perc:
            assert vert_mov != 0 # motor flag should be -1 or 1
        else:
            assert vert_mov == 0 # motor flag should not be set

        time.sleep(0.15)


def test_motor_move_direction(num_checks=20):
    for check_num in range(num_checks):
        horizon, vertical = sun_sensor.get_all_avg()
        horiz_mov, vert_mov = sun_sensor.move_motor()

        if abs(horizon) > move_thresh_perc:
            if horizon < 0.0:
                assert horiz_mov == 1 
            else:
                assert horiz_mov == -1
        else:
            assert horiz_mov == 0 
        if abs(vertical) > move_thresh_perc:
            if vertical > 0.0:
                assert vert_mov == 1 
            else:
                assert vert_mov == -1
        else:
            assert vert_mov == 0 

        time.sleep(0.15)
