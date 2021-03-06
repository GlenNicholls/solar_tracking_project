import sys
import time
import logging
import datetime
from sun_sensor import sun_sensor
from Adafruit_MCP3008 import MCP3008
from utils import utils
from motor_control import MotorCtrl_t as DIRECTION



# init logger
logger_name = 'main_logger'
test_handle = utils(logger_name)
logger = test_handle.init_logger()


# init ADC
CLK        = 21 # BCM pin numbering
MISO       = 19 # BCM pin numbering
MOSI       = 20 # BCM pin numbering
CS         = 10 # BCM pin numbering
NUM_ADC_CH = 8
adc = MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# init sun sensor
adc_vref     = 3.3

mot_move_raw_thresh = 30
north_sens_ch = 6 
east_sens_ch  = 7 
south_sens_ch = 4 
west_sens_ch  = 5 
adc_channels = [north_sens_ch, east_sens_ch, south_sens_ch, west_sens_ch]

ss = sun_sensor( logger_name          = logger_name,
                 logger_module_name   = 'sun_sensor',
                 mot_move_raw_thresh  = mot_move_raw_thresh,
                 adc_volt_ref         = adc_vref,
                 adc_north_sens_ch    = north_sens_ch, 
                 adc_east_sens_ch     = east_sens_ch,  
                 adc_south_sens_ch    = south_sens_ch, 
                 adc_west_sens_ch     = west_sens_ch,  
                 adc_object           = adc
                )


''' Test Routine
'''
def test_sens_channels(num_checks=20):
    string = []

    for _, adc_ch in enumerate(adc_channels):
        string.append('ADC Ch {}'.format(adc_ch))
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []

        for _, adc_ch in enumerate(adc_channels):
            raw_read = adc.read_adc(adc_ch)
            data.append(raw_read)
            assert raw_read > -1 and raw_read < 30 # if negative, BAD! if positive, should not read very high

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)
        time.sleep(0.15)


def test_sun_sensor_differences(num_checks=20):
    string = []

    string.append('Azimuth Diff')
    string.append('Elevation Diff')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []
        az, el = ss.get_diff_all()
        data.append(az)
        data.append(el)

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)

        # TODO: add parameter threshold
        assert abs(az) < mot_move_raw_thresh # unconnected should yield next to zero difference
        assert abs(el) < mot_move_raw_thresh # unconnected should yield next to zero difference

        time.sleep(0.15)


def test_sun_sensor_averages(num_checks=20):
    string = []

    string.append('Avg Azimuth Diff')
    string.append('Avg Elevation Diff')
    max_str_len = len( str(max(string, key=len)) )
    num_cols    = len(string)

    test_handle.write_table(string=string, max_str_len=max_str_len, header=True)

    for check_num in range(num_checks):
        data = []
        az, el = ss.get_avg_all()
        data.append(az)
        data.append(el)

        test_handle.write_table(string=data, max_str_len=max_str_len, header=False)

        # TODO: add parameter threshold
        assert abs(az) < mot_move_raw_thresh  # unconnected should yield next to zero difference
        assert abs(el) < mot_move_raw_thresh  # unconnected should yield next to zero difference

        time.sleep(0.15)


def test_motor_move_flags(num_checks=20):
    for check_num in range(num_checks):
        az_avg, el_av = ss.get_avg_all()
        az_dir, el_dir = ss.get_motor_direction_all()
        logger.info('Azimuth direction: {}'.format(az_dir))
        logger.info('Elevation direction: {}'.format(el_dir))

        if abs(az_avg) > mot_move_raw_thresh:
            assert az_dir != DIRECTION.IDLE # motor flag should be -1 or 1
        else:
            assert az_dir == DIRECTION.IDLE # motor flag should not be set
        if abs(el_av) > mot_move_raw_thresh:
            assert el_dir != DIRECTION.IDLE  # motor flag should be -1 or 1
        else:
            assert el_dir == DIRECTION.IDLE  # motor flag should not be set

        time.sleep(0.15)


def test_motor_move_direction(num_checks=20):
    for check_num in range(num_checks):
        az_avg, el_av = ss.get_avg_all()
        az_dir, el_dir = ss.get_motor_direction_all()
        logger.info('Azimuth direction: {}'.format(az_dir))
        logger.info('Elevation direction: {}'.format(el_dir))

        if abs(az_avg) > mot_move_raw_thresh:
            if az_avg  > 0.0:
                assert az_dir == DIRECTION.WEST 
            else:
                assert az_dir == DIRECTION.EAST
        else:
            assert az_dir == DIRECTION.IDLE 
        if abs(el_av) > mot_move_raw_thresh:
            if el_av > 0.0:
                assert el_dir == DIRECTION.SOUTH 
            else:
                assert el_dir == DIRECTION.NORTH
        else:
            assert el_dir == DIRECTION.IDLE 

        time.sleep(0.15)
