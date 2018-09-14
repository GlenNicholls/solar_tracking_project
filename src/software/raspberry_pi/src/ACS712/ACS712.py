import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008 as ADC

class ACS712(object):
    ''' Class to represent ACS712 current sensor
    '''

    def __init__(self, device_type='ACS712_05B', hardware_spi=True, num_adc_bits=10, vref=3.3, ac_freq=60):
        if device_type.lower == 'acs712_05a':
            self._sensitivity = 0.185
        elif device_type.lower == 'acs712_20a':
            self._sensitivity = 0.100
        elif device_type.lower == 'acs712_30a':
            self._sensitivity = 0.066
        else:
            self._sensitivity = None

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

        self._ADC_res = 2.0**num_adc_bits
        self._Vref = vref
        self._AC_freq = ac_freq
        self._zero = self._ADC_res/2

    def _calibrate(adc_port=0, num_averages=10):
        # ensure that nothing is connected to the current sensor when running this
        # even better, tie input to ground
        for i in range(num_averages):
            self._zero += self._mcp.read_adc(adc_port)
            time.sleep(0.25)
        self._zero /= num_averages
        print('-I- current sensor calibrated successfully')
        return self._zero

    def get_current_DC():
        I = 1.0 * (self._zero - self._mcp.read_adc(adc_port)) / self._ADC_res * self._Vref / self._sensitivity
        return I

    def get_voltage_DC():
        V = 1.0 * self._sensitivity * get_current_DC()
        return V

    def get_power_DC():
        P = 1.0 * get_voltage_DC * get_current_DC()
        return P

    # TBD
    # def get_energy_DC():
    # def get_current_AC():
