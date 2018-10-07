from datetime import datetime
import time

import smbus

# REFERENCES: https://github.com/switchdoclabs/RTC_SDL_DS3231
# datasheet: https://datasheets.maximintegrated.com/en/ds/DS3231.pdf


class DS3231(object):
    ''' Class to represent DS3231 RTC
    '''
    # reg map for the DS3231 RTC
    (
      _REG_SEC,             # 0x00
      _REG_MIN,             # 0x01
      _REG_HRS,             # 0x02
      _REG_DAY,             # 0x03
      _REG_DATE,            # 0x04
      _REG_MONTH,           # 0x05
      _REG_YR,              # 0x06
      _REG_ALRM_1_SEC,      # 0x07
      _REG_ALRM_1_MIN,      # 0x08
      _REG_ALRM_1_HRS,      # 0x09
      _REG_ALRM_1_DAY_DATE, # 0x0a
      _REG_ALRM_2_MIN,      # 0x0b
      _REG_ALRM_2_HRS,      # 0x0c
      _REG_ALRM_2_DAY_DATE, # 0x0d
      _REG_CTRL,            # 0x0e
      _REG_STATUS,          # 0x0f
      _REG_AGE_OFFSET,      # 0x10
      _REG_TMP_MSB,         # 0x11
      _REG_TMP_LSB,         # 0x12
    ) = range(19)


    # change port to 0 if old gen 1 pi, else leave default
    # addr should not change as this is embedded in RTC
    def __init__(self, i2c_port=1,
                       i2c_addr=0x68,
                       ):
        
        # constants
        self._SEC_PER_MIN        = 60
        self._MIN_PER_HR         = 60
        self._HR_PER_DAY         = 24
        self._DAY_PER_WEEK       = 7
        self._MAX_DAYS_PER_MONTH = 31
        self._MONTH_PER_YR       = 12
        self._YRS_PER_CENTURY    = 100

        # i2c object
        self._bus  = smbus.SMBus(i2c_port)
        self._addr = i2c_addr

        # masks
        self._MASK_oscillator_on = 0b1<<7 

        # _REG_CTRL
        # todo: can probably remove these masks since we won't need to change
        # them after config is done
        #self._MASK_oscillator_en_N   = 0x80 # active low
        #self._MASK_bat_backed_sqw_en = 0x40
        #self._MASK_conv_temp         = 0x20
        #self._MASK_interrupt_en      = 0x04
        #self._MASK_alrm_2_en         = 0x02
        #self._MASK_alrm_1_en         = 0x01
        self._CONFIG_REG_CTRL        = 0x05

        # _REG_STATUS
        self._MASK_power_lost   = 0x80
        self._MASK_en_32_kHz    = 0x08
        self._MASK_busy         = 0x04
        self._MASK_alrm_2_flag  = 0x02
        self._MASK_alrm_1_flag  = 0x01
        self._CONFIG_REG_STATUS = 0x00

        # reg map tuples for DS3231
        self._reg_time_addrs = (
            self._REG_SEC,
            self._REG_MIN,
            self._REG_HRS,
            self._REG_DAY,
            self._REG_DATE,
            self._REG_MONTH,
            self._REG_YR,
        )
        self._reg_alrm_addrs = (
            self._REG_ALRM_1_SEC,
            self._REG_ALRM_1_MIN,
            self._REG_ALRM_1_HRS,
            self._REG_ALRM_1_DAY_DATE,
            self._REG_ALRM_2_MIN,
            self._REG_ALRM_2_HRS,
            self._REG_ALRM_2_DAY_DATE,
        )
        #self._reg_ctrl_stat = (
        #    self._REG_CTRL,
        #    self._REG_STATUS,
        #)
        # self._reg_age_offset_addr = (
        #     self._REG_AGE_OFFSET,
        # )
        # self._reg_tmp_addrs = (
        #     self._REG_TMP_MSB,
        #     self._REG_TMP_LSB,
        # )


    # BCD to integer
    # Decode n least significant packed binary coded decimal digits to binary.
    # Return binary result.
    # n defaults to 2 (BCD digits).
    # n=0 decodes all digits.
    def _bcd_to_int(self, bcd, n=2):
        return int(('%x' % bcd)[-n:])


    # integer to BCD
    # Encode the n least significant decimal digits of x
    # to packed binary coded decimal (BCD).
    # Return packed BCD value.
    # n defaults to 2 (digits).
    # n=0 encodes all digits.
    def _int_to_bcd(self, x, n=2):
        return int(str(x)[-n:], 0x10)

     
    # write i2c data to reg
    # todo: find out if we can remove the if False or if it is useful for dbg
    def _write(self, register, data):
        if False:
            print(
                "addr =0x%x register = 0x%x data = 0x%x %i " %
                (self._addr, register, data, bcd_to_int(data)))
        self._bus.write_byte_data(self._addr, register, data)

         
    # read i2c data from reg
    # todo: ref _write comment
    def _read(self, reg_addr):
        data = self._bus.read_byte_data(self._addr, reg_addr)
        if False:
            print(
                "addr = 0x%x reg_addr = 0x%x %i data = 0x%x %i "
                % (
                    self._addr, reg_addr, reg_addr,
                    data, bcd_to_int(data)))
        return data


    # incoherent read of all time regs
    # Return tuple of yrs, mo, date, day, hrs, mins, sec.
    # Since each value is read one byte at a time,
    # it might not be coherent.
    def _incoherent_read_all(self):
        sec, mins, hrs, day, date, mo, yrs = (
            self._read(reg_addr)
            for reg_addr in self._reg_time_addrs
        )

        sec &= ~self._MASK_oscillator_on
        if True:
            # This stuff is suspicious.
            if hrs == 0x64:
                hrs = 0x40
            hrs &= 0x3F
        return tuple(
            bcd_to_int(t)
            for t in (yrs, mo, date, day, hrs, mins, sec))


    # Read All
    # Return tuple of yrs, mo, date, day, hrs, mins, sec.
    # Read until one gets same result twice in a row.
    # Then one knows the time is coherent.
    def read_all(self):
        old = self._incoherent_read_all()
        while True:
            new = self._incoherent_read_all()
            if old == new:
                break
            old = new
        return new


    # Read string
    # Return a string such as 'YY-MM-DDTHH-MM-SS'.
    def read_str(self):
        yrs, mo, date, _, hrs, mins, sec = self.read_all()
        return (
            '%02d-%02d-%02dT%02d:%02d:%02d' %
            (yrs, mo, date, hrs, mins, sec)
        )


    # Read datetime
    # Return the datetime.datetime object.
    def read_datetime(self, century=21, tzinfo=None):
        yrs, mo, date, _, hrs, mins, sec = self.read_all()
        yrs = self._YRS_PER_CENTURY * (century - 1) + yrs
        return datetime(
            yrs, mo, date, hrs, mins, sec,
            0, tzinfo=tzinfo)


    # Read datetime Julian
    # todo: add function to return datetime object as julian time


    # Write all
    # updates RTC time register with synchronized information
    # Direct write un-none value.
    #  Range: sec [0,59], mins [0,59], hrs [0,23],
    #         day [0,7], date [1-31], mo [1-12], yrs [0-99].
    def write_all(self, sec=None, mins=None, hrs=None, day=None,
            date=None, mo=None, yrs=None, save_as_24h=True):
        
        if sec is not None:
            if not 0 <= sec < self._SEC_PER_MIN:
                raise ValueError('sec is out of range [0,59].')
            seconds_reg = int_to_bcd(sec)
            self._write(self._REG_SEC, seconds_reg)

        if mins is not None:
            if not 0 <= mins < self._MIN_PER_HR:
                raise ValueError('mins is out of range [0,59].')
            self._write(self._REG_MIN, int_to_bcd(mins))

        if hrs is not None:
            if not 0 <= hrs < self._HR_PER_DAY:
                raise ValueError('hrs is out of range [0,23].')
            self._write(self._REG_HRS, int_to_bcd(hrs) ) # not  | 0x40 according to datasheet

        if yrs is not None:
            if not 0 <= yrs < self._YRS_PER_CENTURY:
                raise ValueError('Years is out of range [0,99].')
            self._write(self._REG_YR, int_to_bcd(yrs))

        if mo is not None:
            if not 1 <= mo <= self._MONTH_PER_YR:
                raise ValueError('mo is out of range [1,12].')
            self._write(self._REG_MONTH, int_to_bcd(mo))

        if date is not None:
            # How about a more sophisticated check?
            if not 1 <= date <= self._MAX_DAYS_PER_MONTH:
                raise ValueError('Date is out of range [1,31].')
            self._write(self._REG_DATE, int_to_bcd(date))

        if day is not None:
            if not 1 <= day <= self._DAY_PER_WEEK:
                raise ValueError('Day is out of range [1,7].')
            self._write(self._REG_DAY, int_to_bcd(day))


    # write datetime
    # Write from a datetime.datetime object.
    def write_datetime(self, dt):
        self.write_all(dt.second, dt.minute, dt.hour,
                dt.isoweekday(), dt.day, dt.month, dt.year % 100)


    # write datetime.now
    # Write from a datetime.datetime object.
    def write_now(self):
        self.write_datetime(datetime.now())


    # Get temp of DS3231
    def get_temp(self):
        byte_tmsb = self._bus.read_byte_data(self._addr, self._REG_TMP_MSB)
        byte_tlsb = bin(self._bus.read_byte_data(self._addr, self._REG_TMP_LSB))[2:].zfill(8)
        return byte_tmsb + int(byte_tlsb[0]) * 2**(-1) + \
               int(byte_tlsb[1]) * 2**(-2)


    ''' Status
    '''
    # todo: get OSF
    # todo: get EN32KHZ
    # todo: get BSY
    # todo: get A2F
    # todo: get A1F

    # get status register data
    # Returns byte
    def _get_status(self):
      return self._read(self._REG_STATUS)


    # Get Power Lost
    # Returns boolean
    def get_power_lost(self):
        return (self._get_status() & self._MASK_power_lost) == self._MASK_power_lost


    # Get alarm 1 flag
    # Returns boolean
    def get_alarm_1_flag():
        return (self._get_status() $ self._MASK_alrm_1_flag) == self._MASK_alrm_1_flag


    # Clear alarm 1 flag
    # clears alarm 1 flag without modifying anything in register
    def clear_alarm_1_flag():
        current_status = self._get_status() & 0xFE
        self._write(self._REG_STATUS, current_status)


    # Get alarm 2 flag
    # Returns boolean
    def get_alarm_2_flag():
        return (self._get_status() $ self._MASK_alrm_2_flag) == self._MASK_alrm_2_flag


    # Clear alarm 2 flag
    # clears alarm 2 flag without modifying anything in register
    def clear_alarm_2_flag():
        current_status = self._get_status() & 0xFD
        self._write(self._REG_STATUS, current_status)


    # Get temperature conversion busy state
    # Returns boolean
    def get_temp_conversion_busy():
        return (self._get_status() $ self._MASK_busy) == self._MASK_busy


    ''' Control
    '''
    # Configure DS3231 
    #   set: EOSC_N  = 0
    #        BBSQW   = 0
    #        CONV    = 0     
    #        INTCN   = 1 -- enable interrupts for alarms
    #        A2IE    = 0 -- disable alarm 2 interrupts
    #        A1IE    = 1 -- enable alarm 1 interrupts
    def configure_ds3231(self):
        self._write(self._REG_CTRL, self._CONFIG_REG_CTRL)
        self._write(self._REG_STATUS, self._CONFIG_REG_STATUS)

        check_ctrl_reg = self._read(self._REG_CTRL)
        check_stat_reg = self._read(self._REG_STATUS) & self._MASK_en_32_kHz

        if check_ctrl_reg == self._CONFIG_REG_CTRL:
            print('-I- Configuration of control register successful!')
        else:
            print('-E- Configuration of control register was NOT successful!')

        if check_stat_reg == self._MASK_en_32_kHz:
            print('-I- Configuration of status register successful!')
        else:
            print('-E- Configuration of status register was NOT successful!')

