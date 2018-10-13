import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008 as ADC

# todo: refactor this to something like adc_monitor
#       and use enums for the device on each adc channel
class ACS712(object):
    ''' Class to represent ACS712 current sensor
    '''

    # naming convenction:
    # ACS712 : device part number
    # _XX    : device current rating
    # A      : current unit [Amps]
    # U | B  : unidirectional or bidirectional
    def __init__(self, device_type  = 'ACS712_05AB',
                       vref         = 3.3, 
                       ac_freq      = 60,
                       num_adc_bits = 10, 
                       adc_channel  = 0,
                       num_cal_avgs = 20,
                       hardware_spi = True, # todo: add ability to define GPIO if not using HW spi 
                       ):                   #       also add ability to select which SPI port we're using

        self._ADC_res = 2.0**num_adc_bits

        # set zero point based on device
        if device_type.lower().find('ab') > -1: # if bidirectional current sensot, our zero is ADC_resolution/2
            self._zero = self._ADC_res/2
        elif device_type.lower().find('au') > -1: # if unidirectional, zero is 0
            self._zero = 0
        else:
            self._zero = None

        # set device sensitivity
        if device_type.lower() == 'acs712_05au' or device_type.lower() == 'acs712_05ab':
            self._sensitivity = 0.185
        elif device_type.lower() == 'acs712_20au' or device_type.lower() == 'acs712_20ab':
            self._sensitivity = 0.100
        elif device_type.lower() == 'acs712_30au' or device_type.lower() == 'acs712_30ab':
            self._sensitivity = 0.066
        else:
            self._sensitivity = None

        # ensure valid enteries from user
        if self._sensitivity == None or self._zero == None:
            print('-E- Invalid current sensing device! You entered: {}'.format(device_type))
            print('-E- Valid inputs are: ACS712_05AB, ACS712_05AU, ACS712_20AB, ACS712_20AU, ACS712_30AB, or ACS712_30AU')
            return

        # todo: abstract this at some point to give dynamic control at top level
        # todo: abstract this procedure to use any ADC by grabbing functions/objects passed in
        # determine if we are using HW or SW SPI
        if hardware_spi:
            self.SPI_PORT   = 0
            self.SPI_DEVICE = 0
            self._mcp = ADC.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))
        # todo: make this a tuple or something that is passed in
        else:
            CLK  = 18
            MISO = 23
            MOSI = 24
            CS   = 25
            self._mcp = ADC.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
        
        # set constants
        self._Vref         = vref
        self._AC_freq      = ac_freq
        self._ADC_channel  = adc_channel
        self._Num_cal_avgs = num_cal_avgs
        self._ADC_scale    = 1.0 / self._ADC_res * self._Vref / self._sensitivity


    def _read_adc_raw(self):
        return self._mcp.read_adc(self._ADC_channel)


    # don't need to run calibration routine, if this is the case, zero will be set to 0 for unidirectional
    # and Fs/2 for bidirectional
    def calibrate_current_sensor(self):
        # ensure that nothing is connected to the current sensor when running this
        # even better, tie input to ground
        for i in range(self._Num_cal_avgs - 1):
            self._zero += self._mcp.read_adc(self._ADC_channel)
            time.sleep(0.25)
        self._zero /= self._Num_cal_avgs
        print('-I- current sensor calibrated successfully')


    # todo: pass in channel as variable
    def get_current_DC(self):
        I = 1.0 * (self._zero - self._read_adc_raw()) * self._ADC_scale 
        return float(I)


    # todo: refactor below to read adc based on port
    # todo: pass in channel as variable
    def __get_voltage_DC(self):
        V = 1.0 * self._sensitivity * self.get_current_DC()
        return float(V)


    def __get_power_DC(self):
        P = 1.0 * self.get_voltage_DC() * self.get_current_DC()
        return float(P)

    # TBD
    # def get_energy_DC():
    # def get_current_AC():
