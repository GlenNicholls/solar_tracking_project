# from datetime import datetime, timedelta
import datetime
from datetime import timedelta
from dateutil import tz 
import time
import logging
import astral
import smbus
from enum import Enum, unique

# REFERENCES: https://github.com/switchdoclabs/RTC_SDL_DS3231
#             https://pypi.org/project/astral/1.2/
#
# datasheet:  https://datasheets.maximintegrated.com/en/ds/DS3231.pdf


@unique
class AlrmType_t(Enum):
    ALM1_EVERY_SECOND  = 0x0F
    ALM1_MATCH_SECONDS = 0x0E
    ALM1_MATCH_MINUTES = 0x0C #  match minutes *and* seconds
    ALM1_MATCH_HOURS   = 0x08 #  match hours *and* minutes, seconds
    ALM1_MATCH_DATE    = 0x00 #  match date *and* hours, minutes, seconds
    ALM1_MATCH_DAY     = 0x10 #  match day *and* hours, minutes, seconds
    ALM2_EVERY_MINUTE  = 0x8E
    ALM2_MATCH_MINUTES = 0x8C #  match minutes
    ALM2_MATCH_HOURS   = 0x88 #  match hours *and* minutes
    ALM2_MATCH_DATE    = 0x80 #  match date *and* hours, minutes
    ALM2_MATCH_DAY     = 0x90 #  match day *and* hours, minutes


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
    def __init__(self, logger='main_logger',
                       i2c_port  = 1,
                       i2c_addr  = 0x68,
                       latitude  = 0.00,
                       longitude = 0.00
                       ):
        # instantiate logger
        self.logger = logging.getLogger(logger+ '.' + __name__)
        self.logger.info('creating an instance of the {}'.format(__name__))
        
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

        # coordinates
        self._latitude  = latitude
        self._longitude = longitude

        # masks
        self._MASK_oscillator_on = 0b1<<7 

        # _REG_CTRL
        # todo: can probably remove these masks since we won't need to change
        # them after config is done
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
        self._reg_alrm_1_addrs = (
            self._REG_ALRM_1_SEC,
            self._REG_ALRM_1_MIN,
            self._REG_ALRM_1_HRS,
            self._REG_ALRM_1_DAY_DATE,
            )
        self._reg_alrm_2_addrs = (
            self._REG_ALRM_2_MIN,
            self._REG_ALRM_2_HRS,
            self._REG_ALRM_2_DAY_DATE,
            )


    ''' _____ Private Members _____
    '''
    '''
    '''

    ''' Helper functions
    '''
    # BCD to integer
    # Decode n least significant packed binary coded decimal digits to binary.
    # Return binary result.
    # n defaults to 2 (BCD digits).
    # n=0 decodes all digits.
    def __bcd_to_int(self, bcd, n=2):
        bcd2int = int(('%x' % bcd)[-n:])
        self.logger.debug('BCD to Int: {}'.format(bcd2int))
        return bcd2int


    # integer to BCD
    # Encode the n least significant decimal digits of x
    # to packed binary coded decimal (BCD).
    # Return packed BCD value.
    # n defaults to 2 (digits).
    # n=0 encodes all digits.
    def __int_to_bcd(self, x, n=2):
        int2bcd = int(str(x)[-n:], 0x10)
        self.logger.debug('Int to BCD: {}'.format(int2bcd))
        return int2bcd

    # utc to local time
    def __utc_to_local(self, utc):
        # Auto-detect zone
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()

        # convert time zone
        central = utc.astimezone(to_zone)

        self.logger.debug('Converting UTC to Local time')
        self.logger.debug('From Zone: {}, To Zone: {}'.format(from_zone,to_zone))
        self.logger.debug('Central Time: {}'.format(central))
        return central


    # write i2c data to reg
    # todo: find out if we can remove the if False or if it is useful for dbg
    def __write(self, register, data):
        if False:
            print(
                "addr =0x%x register = 0x%x data = 0x%x %i " %
                (self._addr, register, data, self.__bcd_to_int(data)))
        self._bus.write_byte_data(self._addr, register, data)

         
    # read i2c data from reg
    # todo: ref __write comment
    def __read(self, reg_addr):
        data = self._bus.read_byte_data(self._addr, reg_addr)
        if False:
            self.logger.error('Invalid I2C Read State!')
            print(
                "addr = 0x%x reg_addr = 0x%x %i data = 0x%x %i "
                % (
                    self._addr, reg_addr, reg_addr,
                    data, self.__bcd_to_int(data)))
        self.logger.debug('I2C read cmd: {}'.format(reg_addr))
        self.logger.debug('I2C read from addr: {}'.format(self._addr))
        self.logger.debug('I2C read data: {}'.format(data))
        return data


    ''' Time Registers
    '''
    # incoherent read of all time regs
    # Return tuple of yrs, month, date, day, hrs, mins, sec.
    # Since each value is read one byte at a time,
    # it might not be coherent.
    def __incoherent_read_all(self):
        sec, mins, hrs, day, date, month, yrs = (
            self.__read(reg_addr)
            for reg_addr in self._reg_time_addrs
        )

        sec &= ~self._MASK_oscillator_on
        if True:
            # This stuff is suspicious.
            if hrs == 0x64:
                hrs = 0x40
            hrs &= 0x3F
        return_data = tuple(
            self.__bcd_to_int(t)
            for t in (yrs, month, date, day, hrs, mins, sec))
        self.logger.debug('Incoherent read all data regs returns: {}'.format(return_data))
        return return_data 


    # Write all
    # updates RTC time register with synchronized information
    # Direct write un-none value.
    #  Range: sec [0,59], mins [0,59], hrs [0,23],
    #         day [0,7], date [1-31], month [1-12], yrs [0-99].
    def __write_all_time_regs(self, sec=None, mins=None, hrs=None, day=None,
            date=None, month=None, yrs=None, save_as_24h=True):
        self.logger.debug('Performing write to all RTC time regs')
        
        if sec is not None:
            if not 0 <= sec < self._SEC_PER_MIN:
                raise ValueError('sec is out of range [0,59].')
            seconds_reg = self.__int_to_bcd(sec)
            self.__write(self._REG_SEC, seconds_reg)

        if mins is not None:
            if not 0 <= mins < self._MIN_PER_HR:
                raise ValueError('mins is out of range [0,59].')
            self.__write(self._REG_MIN, self.__int_to_bcd(mins))

        if hrs is not None:
            if not 0 <= hrs < self._HR_PER_DAY:
                raise ValueError('hrs is out of range [0,23].')
            self.__write(self._REG_HRS, self.__int_to_bcd(hrs) ) # not  | 0x40 according to datasheet

        if yrs is not None:
            if not 0 <= yrs < self._YRS_PER_CENTURY:
                raise ValueError('Years is out of range [0,99].')
            self.__write(self._REG_YR, self.__int_to_bcd(yrs))

        if month is not None:
            if not 1 <= month <= self._MONTH_PER_YR:
                raise ValueError('month is out of range [1,12].')
            self.__write(self._REG_MONTH, self.__int_to_bcd(month))

        if date is not None:
            # How about a more sophisticated check?
            if not 1 <= date <= self._MAX_DAYS_PER_MONTH:
                raise ValueError('Date is out of range [1,31].')
            self.__write(self._REG_DATE, self.__int_to_bcd(date))

        if day is not None:
            if not 1 <= day <= self._DAY_PER_WEEK:
                raise ValueError('Day is out of range [1,7].')
            self.__write(self._REG_DAY, self.__int_to_bcd(day))


    # write datetime
    # Write from a datetime.datetime object.
    def __set_datetime(self, dt):
        self.__write_all_time_regs(dt.second, dt.minute, dt.hour,
                dt.isoweekday(), dt.day, dt.month, dt.year % 100)
        self.logger.debug('Setting RTC with datetime object: {}'.format(dt))


    # Read All
    # Return tuple of yrs, month, date, day, hrs, mins, sec.
    # Read until one gets same result twice in a row.
    # Then one knows the time is coherent.
    def __get_all_time_regs(self):
        old = self.__incoherent_read_all()
        while True:
            new = self.__incoherent_read_all()
            if old == new:
                break
            self.logger.warning('Reading RTC time regs is on second boundry, trying again')
            old = new

        self.logger.warning('Reading RTC time regs is stable, seeing: {}'.format(new))
        return new


    # Read datetime Julian
    # todo: add function to return datetime object as julian time



    ''' Alarm Registers
    '''
    # set the alarm
    # has_seconds should be false for alarm 2
    def __set_alrm_regs(self, alrm_type=None, sec=None, mins=None, hrs=None, daydate=None):
        self.logger.debug('Setting RTC alarm regs')

        if not isinstance(alrm_type, AlrmType_t): #alrm_type not in AlrmType_t:
            raise ValueError('Alarm Type is not in enumerate')

        if sec is not None:
            if not 0 <= sec < self._SEC_PER_MIN:
                raise ValueError('sec is out of range [0,59].')
            seconds = self.__int_to_bcd(sec)

        if mins is not None:
            if not 0 <= mins < self._MIN_PER_HR:
                raise ValueError('mins is out of range [0,59].')
            minutes = self.__int_to_bcd(mins)

        if hrs is not None:
            if not 0 <= hrs < self._HR_PER_DAY:
                raise ValueError('hrs is out of range [0,23].')
            hours   = self.__int_to_bcd(hrs)

        if daydate is not None:
            # todo: create better check here
            #if not 1 <= date <= self._MAX_DAYS_PER_MONTH:
            if False:
                raise ValueError('Date is out of range [1,31].')
            daydate = self.__int_to_bcd(daydate)
        
        self.logger.debug('Alarm Type: {}'.format(alrm_type.name))
        self.logger.debug('Alarm Value: {}'.format(alrm_type.value))

        if (alrm_type.value & 0x01): # A1M1
            seconds |= 0b1<<7  
            self.logger.debug('Setting mode A1M1')
        if (alrm_type.value & 0x02): # A1M2
            minutes |= 0b1<<7
            self.logger.debug('Setting mode A1M2')
        if (alrm_type.value & 0x04): # A1M3
            hours |= 0b1<<7
            self.logger.debug('Setting mode A1M3')
        if (alrm_type.value & 0x10): # DYDT
            daydate |= 0b1<<6
            self.logger.debug('Setting mode Day Date')
        if (alrm_type.value & 0x08): # A1M4
            daydate |= 0b1<<7
            self.logger.debug('Setting mode A1M4')

        if ~(alrm_type.value & 0x80): # alarm 1
            data = (seconds, minutes, hours, daydate)
            for i, reg in enumerate(self._reg_alrm_1_addrs):
                self.__write(reg, data[i])
            self.logger.debug('Setting RTC Alarm 1 for up to seconds match of datetime: {}'.format(data))
        else: # alarm 2
            data = (minutes, hours, daydate)
            for i, reg in enumerate(self._reg_alrm_2_addrs):
                self.__write(reg, data[i])    
            self.logger.debug('Setting RTC Alarm 2 for up to minutes match of datetime: {}'.format(data))


    # Set alarm with datetime object
    def __set_alrm_datetime(self, dt):
        self.__set_alrm_regs(AlrmType_t.ALM1_MATCH_DATE, dt.second, dt.minute,
                            dt.hour, dt.day)
        self.logger.debug('Setting alarm with datetime object')



    ''' Status Register
    '''
    # get status register data
    # Returns byte
    def __get_status(self):
        status_reg = self.__read(self._REG_STATUS)
        self.logger.debug('Checking RTC status register: {}'.format(status_reg))
        return status_reg    


    ''' _____ Public Members _____
    '''
    '''
    '''
    # Configure DS3231 
    #   set: EOSC_N  = 0
    #        BBSQW   = 0
    #        CONV    = 0     
    #        INTCN   = 1 -- enable interrupts for alarms
    #        A2IE    = 0 -- disable alarm 2 interrupts
    #        A1IE    = 1 -- enable alarm 1 interrupts
    def configure_rtc(self):
        self.logger.info('Configuring Status and Control Registers')
        self.__write(self._REG_CTRL, self._CONFIG_REG_CTRL)
        self.__write(self._REG_STATUS, self._CONFIG_REG_STATUS)

        check_ctrl_reg = self.__read(self._REG_CTRL)
        check_stat_reg = self.__read(self._REG_STATUS) & self._MASK_en_32_kHz

        if check_ctrl_reg == self._CONFIG_REG_CTRL:
            self.logger.info('Configuration of control register successful!')
        else:
            self.logger.error('Configuration of control register was NOT successful!')
            raise ValueError
        self.logger.info('Control Reg Value: 0b{:08b}, Expected Value: 0b{:08b}'.format(check_ctrl_reg, self._CONFIG_REG_CTRL))

        if check_stat_reg == self._CONFIG_REG_STATUS:
            self.logger.info('Configuration of status register successful!')
        else:
            self.logger.error('Configuration of status register was NOT successful!')
            raise ValueError
        self.logger.info('Status Reg Value: 0b{:08b}, Expected Value: 0b{:08b}'.format(check_stat_reg, self._CONFIG_REG_STATUS))


    # Read string
    # Return a string such as 'YY-MM-DD HH:MM:SS'.
    def get_datetime_str(self):
        yrs, month, date, _, hrs, mins, sec = self.__get_all_time_regs()
        return (
            '%02d-%02d-%02d %02d:%02d:%02d' %
            (yrs, month, date, hrs, mins, sec)
        )


    # Read datetime
    # Return the datetime.datetime object.
    def get_datetime(self, century=21, tzinfo=None):
        time_str = self.get_datetime_str()
        self.logger.debug('RTC datetime as string: {}'.format(time_str))
        return datetime.datetime.strptime(time_str, "%y-%m-%d %H:%M:%S")


    # get datetime timedelta
    # return tuple of difference between RTC datetime and datetime.datetime.now
    def get_datetime_delta(self):
        rtc_datetime = self.get_datetime()
        local_now = datetime.datetime.now()
        delta = local_now - rtc_datetime
        self.logger.debug('RTC datetime: {}'.format(rtc_datetime))
        self.logger.debug('Local Time: {}'.format(local_now))
        self.logger.debug('RTC and Local time delta: {}'.format(delta))
        return delta


    # write datetime.now
    # Write from a datetime.datetime object.
    def set_datetime_now(self):
        dt = datetime.datetime.now()
        self.__set_datetime(datetime.datetime.now(dt))
        self.logger.debug('Setting RTC time to datetime.now(): {}'.format())


    # Set alarm
    # sets an alarm for now + the specified number of days, hours, minutes, and seconds
    def set_alarm_now_delta(self, days=0, hours=0, minutes=0, seconds=0):
        if days == hours == minutes == seconds == 0:
            self.logger.error('Not entering delta may cause RTC to become unstable!')
            raise ValueError('Due to time passing, not entering any timedelta might cause RTC to become unstable')
        now   = datetime.datetime.now()
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        time  = now + delta 
        self.__set_alrm_datetime(time)
        self.logger.info('Setting RTC alarm with delta: {}'.format(delta))
        self.logger.info('RTC alarm is set for: {}'.format(time))


    # set alarm sunrise
    # sets an alarm for the sunrise date/time
    def set_alarm_sunrise(self):
        # todo: convert from utc to local unless full system uses utc
        next_day = datetime.datetime.now() + timedelta(days=1)
        next_day_date = next_day.date()
        time_utc = astral.Astral.sunrise_utc(next_day_date, self._latitude, self._longitude)
        time_local = self.__utc_to_local(time_utc)
        self.__set_alrm_datetime(time_local)
        self.logger.debug('1 day from now is: {}'.format(next_day))
        self.logger.debug('Date for tomorrow is: {}'.format(next_day_date))
        self.logger.debug('UTC time call is: {}, local conversion: {}'.format(time_utc, time_local))
        self.logger.info('Setting sunrise alarm for: {}'.format(time_local))


    # todo: add function for checking when sunset is


    # Get Power Lost
    # Returns boolean
    def get_power_lost(self):
        self.debug('Checking to see if power was lost')
        power_lost = bool(self.__get_status() & self._MASK_power_lost)
        if power_lost:
            self.logger.warning('Power was lost, check the battery and power supply')
        return power_lost 


    # Get alarm 1 flag
    # Returns boolean
    def get_alarm_1_flag(self):
        alrm_set = bool(self.__get_status() & self._MASK_alrm_1_flag)
        if alrm_set:
            self.debug('RTC Alarm 1 is set')
        else:
            self.debug('RTC Alarm 1 is NOT set')
        return alrm_set


    # Clear alarm 1 flag
    # clears alarm 1 flag without modifying anything in register
    def clear_alarm_1_flag(self):
        self.debug('Clearing RTC alarm 1 flag')
        current_status = self.__get_status() & 0xFE
        self.__write(self._REG_STATUS, current_status)


    # Get alarm 2 flag
    # Returns boolean
    def get_alarm_2_flag(self):
        alrm_set = bool(self.__get_status() & self._MASK_alrm_2_flag)
        if alrm_set:
            self.debug('RTC Alarm 2 is set')
        else:
            self.debug('RTC Alarm 2 is NOT set')
        return alrm_set


    # Clear alarm 2 flag
    # clears alarm 2 flag without modifying anything in register
    def clear_alarm_2_flag():
        self.debug('Clearing RTC alarm 2 flag')
        current_status = self.__get_status() & 0xFD
        self.__write(self._REG_STATUS, current_status)


    # Check and clear both alarms
    # return boolean
    # asserts true if either alarm was set
    def check_and_clear_alarms(self):
        self.debug('Checking both RTC alarm flags')
        is_alarm = False
        if self.get_alarm_1_flag():
            is_alarm = True
            self.clear_alarm_1_flag()
        if self.get_alarm_2_flag():
            is_alarm = True
            self.clear_alarm_2_flag()
        return is_alarm


    # Get temperature conversion busy state
    # Returns boolean
    def get_temp_conversion_busy():
        conv_busy = bool(self.__get_status() & self._MASK_busy)
        if conv_busy:
            self.debug('RTC Temperature is busy')
        else:
            self.debug('RTC Temperature is NOT busy')
        return conv_busy


    # Get temp of DS3231
    # todo: add support for starting a new conversion, this doesn't appear to 
    #       update the value, either that or it is very stable where I'm testing
    def get_temp(self):
        byte_tmsb = self._bus.read_byte_data(self._addr, self._REG_TMP_MSB)
        byte_tlsb = bin(self._bus.read_byte_data(self._addr, self._REG_TMP_LSB))[2:].zfill(8)
        temp_C = byte_tmsb + int(byte_tlsb[0]) * 2**(-1) + int(byte_tlsb[1]) * 2**(-2)
        self.logger.debug('Temp MSB: {}, Temp LSB: {}'.format(byte_tmsb, byte_tlsb))
        self.logger.debug('RTC Temperature: {} \'C'.format(temp_C))
        return temp_C 



