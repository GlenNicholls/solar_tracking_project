import time
import logging


class power_measurement(object):
    
    def __init__(self, logger                = 'main_logger',
                       volt_ref              = 3.3,
                       num_adc_bits          = 10,
                       adc_current_channels  = (0,1),
                       adc_voltage_channels  = (2,3),
                       adc_object            = None
                 ):

        # instantiate logger
        self.logger = logging.getLogger(logger+ '.' + __name__)
        self.logger.info('creating an instance of the {}'.format(__name__))

        # set adc resolution
        self._ADC_res = 2.0**num_adc_bits

        # capture internal config
        self._v_ref        = volt_ref
        self._num_adc_bits = num_adc_bits
        
        # ADC
        self._curr_ch = adc_current_channels
        self._volt_ch = adc_voltage_channels
        self._adc    = adc_object
        
        if len(self._curr_ch + self._volt_ch) > len(set(self._curr_ch + self._volt_ch)): # appending tuples to check for uniqueness
            self.logger.error('ADC channels are not unique!')
            raise ValueError('ADC channels are not unique!')
        if adc_object == None:
            self.logger.error('No ADC object passed by reference!')
            raise ValueError('No ADC object passed by reference!')


    def __meas_adc_voltage(self):
    
    # current measurement
    # current=(Vmeas/Gain)**2/R_shunt
    def get_current_A(self):

    # voltage measurement
    # Vsrc = (R2+R1)/R2*Vmeas
    def get_voltage_V(self):

    def get_power_W(self):

    def get_energy_(self):
    
    def get_all_measurements(self):
