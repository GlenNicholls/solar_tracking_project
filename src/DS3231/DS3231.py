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
      _reg_sec,             # 0x00
      _reg_min,             # 0x01
      _reg_hrs,             # 0x02
      _reg_day,             # 0x03
      _reg_date,            # 0x04
      _reg_mo,              # 0x05
      _reg_yr,              # 0x06
      _reg_alrm_1_sec,      # 0x07
      _reg_alrm_1_min,      # 0x08
      _reg_alrm_1_hrs,      # 0x09
      _reg_alrm_1_day_date, # 0x0a
      _reg_alrm_2_min,      # 0x0b
      _reg_alrm_2_hrs,      # 0x0c
      _reg_alrm_2_day_date, # 0x0d
      _reg_ctrl,            # 0x0e
      _reg_status,          # 0x0f
      _reg_age_offset,      # 0x10
      _reg_tmp_msb,         # 0x11
      _reg_tmp_lsb,         # 0x12
    ) = range(19)


    # change port to 0 if old gen 1 pi, else leave default
    # addr should not change as this is embedded in RTC
    def __init__(self, i2c_port=1,
                       i2c_addr=0x68,
                       ):
        
        # constants
        self._sec_per_min     = 60
        self._min_per_hr      = 60
        self._hr_per_day      = 24
        self._day_per_week    = 7
        self._max_days_per_mo = 31
        self._mo_per_yr       = 12
        self._yr_per_century  = 100

        # masks
        self._oscillator_on_mask = 0b1<<7 # _reg_ctrl
        self._power_lost_mask    = 0b1<<7 # _reg_status

        # i2c object
        self._bus  = smbus.SMBus(i2c_port)
        self._addr = i2c_addr

        # reg map tuples for DS3231
        self._reg_time_addrs = (
            self._reg_sec,
            self._reg_min,
            self._reg_hrs,
            self._reg_day,
            self._reg_date,
            self._reg_mo,
            self._reg_yr,
        )
        self._reg_alrm_addrs = (
            self._reg_alrm_1_sec,
            self._reg_alrm_1_min,
            self._reg_alrm_1_hrs,
            self._reg_alrm_1_day_date,
            self._reg_alrm_2_min,
            self._reg_alrm_2_hrs,
            self._reg_alrm_2_day_date,
        )
        self._reg_ctrl_stat = (
            self._reg_ctrl,
            self._reg_status,
        )
        # self._reg_age_offset_addr = (
        #     self._reg_age_offset,
        # )
        # self._reg_tmp_addrs = (
        #     self._reg_tmp_msb,
        #     self._reg_tmp_lsb,
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

        sec &= ~self._oscillator_on_mask
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
        yrs = self._yr_per_century * (century - 1) + yrs
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
            if not 0 <= sec < self._sec_per_min:
                raise ValueError('sec is out of range [0,59].')
            seconds_reg = int_to_bcd(sec)
            self._write(self._reg_sec, seconds_reg)

        if mins is not None:
            if not 0 <= mins < self._min_per_hr:
                raise ValueError('mins is out of range [0,59].')
            self._write(self._reg_min, int_to_bcd(mins))

        if hrs is not None:
            if not 0 <= hrs < self._hr_per_day:
                raise ValueError('hrs is out of range [0,23].')
            self._write(self._reg_hrs, int_to_bcd(hrs) ) # not  | 0x40 according to datasheet

        if yrs is not None:
            if not 0 <= yrs < self._yr_per_century:
                raise ValueError('Years is out of range [0,99].')
            self._write(self._reg_yr, int_to_bcd(yrs))

        if mo is not None:
            if not 1 <= mo <= self._mo_per_yr:
                raise ValueError('mo is out of range [1,12].')
            self._write(self._reg_mo, int_to_bcd(mo))

        if date is not None:
            # How about a more sophisticated check?
            if not 1 <= date <= self._max_days_per_mo:
                raise ValueError('Date is out of range [1,31].')
            self._write(self._reg_date, int_to_bcd(date))

        if day is not None:
            if not 1 <= day <= self._day_per_week:
                raise ValueError('Day is out of range [1,7].')
            self._write(self._reg_day, int_to_bcd(day))


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
        byte_tmsb = self._bus.read_byte_data(self._addr, self._reg_tmp_msb)
        byte_tlsb = bin(self._bus.read_byte_data(self._addr, self._reg_tmp_lsb))[2:].zfill(8)
        return byte_tmsb + int(byte_tlsb[0]) * 2**(-1) + \
               int(byte_tlsb[1]) * 2**(-2)


    ''' Control
    '''
    # todo: set oscillator EOSC
    # todo: set BBSQW
    # todo: set CONV
    # todo: set INTCN
    # todo: set A2IE
    # todo: set A1IE

    ''' Status
    '''
    # todo: get OSF
    # todo: get EN32KHZ
    # todo: get BSY
    # todo: get A2F
    # todo: get A1F
