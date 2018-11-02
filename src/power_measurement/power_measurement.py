import time
import logging


class power_measurement(object):

    def __init__(self, logger       = 'main_logger',
                       volt_ref     = 3.3,
                       num_adc_bits = 10,
                 ):

        # instantiate logger
        self.logger = logging.getLogger(logger+ '.' + __name__)
        self.logger.info('creating an instance of the {}'.format(__name__))

        # set adc resolution
        self._ADC_res = 2.0**num_adc_bits

        # capture internal config
        self._v_ref        = volt_ref
        self._num_adc_bits = num_adc_bits


    def get_current_A(self, adc_raw):

    def get_voltage_V(self, adc_raw):

    def get_power_W(self, adc_raw):

    def get_energy_(self, adc_raw):
