import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008 as ADC

class ACS712(object):
    ''' Class to represent ACS712 current sensor
    '''

    # naming convenction:
    # ACS712 : device part number
    # _XX    : device current rating
    # A      : current unit [Amps]
    # U | B  : unidirectional or bidirectional
    def __init__(self, device_type='ACS712_05AB',
                       vref=3.3, 
                       ac_freq=60,
                       num_adc_bits=10, 
                       adc_port=0,
                       num_cal_avgs=20,
                       hardware_spi=True, 
                       ):
        if device_type.lower.find('ab') > -1: # if bidirectional current sensot, our zero is ADC_resolution/2
            self._zero = self._ADC_res/2
        elif device_type.lower.find('au') > -1: # if unidirectional, zero is 0
            self._zero = 0
        else:
            print('-E- you have not specified a valid device current sensing polarity, reference documentation')
            print('-E- valid inputs are: ACS712_05AB, ACS712_05AU, ACS712_20AB, ACS712_20AU, ACS712_30AB, or ACS712_30AU')
            self._zero = None

        if device_type.lower == 'acs712_05au' or device_type.lower == 'acs712_05ab':
            self._sensitivity = 0.185
        elif device_type.lower == 'acs712_20au' or device_type.lower == 'acs712_20ab':
            self._sensitivity = 0.100
        elif device_type.lower == 'acs712_30au' or device_type.lower == 'acs712_30ab':
            self._sensitivity = 0.066
        else:
            print('-E- you have not specified a valid device current sensing polarity, reference documentation')
            print('-E- valid inputs are: ACS712_05AB, ACS712_05AU, ACS712_20AB, ACS712_20AU, ACS712_30AB, or ACS712_30AU')
            self._sensitivity = None

        # todo: abstract this at some point to give dynamic control at top level
        # todo: abstract this procedure to use any ADC by grabbing functions/objects passed in
        if hardware_spi:
            self.SPI_PORT   = 0
            self.SPI_DEVICE = 0
            self._mcp = ADC.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))
        else:
            CLK  = 18
            MISO = 23
            MOSI = 24
            CS   = 25
            self._mcp = ADC.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

        self._Vref         = vref
        self._AC_freq      = ac_freq
        self._ADC_res      = 2.0**num_adc_bits
        self._ADC_port     = adc_port
        self._Num_cal_avgs = num_cal_avgs
        

    # don't need to run calibration routine, if this is the case, zero will be set to 0 for unidirectional
    # and Fs/2 for bidirectional
    def _calibrate(self):
        # ensure that nothing is connected to the current sensor when running this
        # even better, tie input to ground
        for i in range(self._Num_cal_avgs):
            self._zero += self._mcp.read_adc(self._ADC_port)
            time.sleep(0.25)
        self._zero /= num_averages
        print('-I- current sensor calibrated successfully')
        return self._zero


    def get_current_DC(self):
        I = 1.0 * (self._zero - self._mcp.read_adc(adc_port)) / self._ADC_res * self._Vref / self._sensitivity
        return I


    def get_voltage_DC(self):
        V = 1.0 * self._sensitivity * get_current_DC()
        return V


    def get_power_DC(self):
        P = 1.0 * get_voltage_DC * get_current_DC()
        return P

    # TBD
    # def get_energy_DC():
    # def get_current_AC():
