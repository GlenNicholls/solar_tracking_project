import time
import logging
import RPi.GPIO as MOT
from enum import Enum, unique

@unique
class MotorCtrl_t(Enum):
  IDLE    = -1 # so we don't move and if it gets passed to motor move, an error will be raised
  WEST    = 0
  NORTH   = 1
  EAST    = 2
  SOUTH   = 3


class stepper_motor(object):

  def __init__(self, logger_name          = 'main_logger', 
                     logger_module_name   = 'stepper_motor',
                     pin_elevation        = None,
                     pin_azimuth          = None,
                     pin_direction        = None,
                     pin_clock            = None,
                     pin_reset            = None,
                     pin_lim_sw_azimuth   = None,
                     pin_lim_sw_elevation = None,
                     az_steps_per_deg     = None,
                     el_steps_per_deg     = None
               ):
    # instantiate logger
    self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
    self.logger.info('creating an instance of the {}'.format(logger_module_name))

    self._speed   = 0.001 # hardcoding here as don't want sys to unintentionally become unstable
    self._ENABLE  = 1
    self._DISABLE = 0

    # define pin numbers
    self._dir    = pin_direction
    self._el     = pin_elevation
    self._clk    = pin_clock
    self._az     = pin_azimuth
    self._rst    = pin_reset
    self._lim_az = pin_lim_sw_azimuth
    self._lim_el = pin_lim_sw_elevation
    
    # create pin tuple to ensure uniqueness
    self._pin_t = (self._dir, self._el, self._clk, self._az, self._rst, self._lim_az, self._lim_el)
    
    if len(self._pin_t) > len(set(self._pin_t)):
      print(self._pint_t)
      raise ValueError('GPIO pin numbers must be unique integers!')
    for _, pin in enumerate(self._pin_t):
      if pin == None or type(pin) != int:
        raise ValueError('GPIO {} must be an integer!'.format(pin))
    
    # steps per degree
    self._deg_az = az_steps_per_deg
    self._deg_el = el_steps_per_deg
    
    if self._deg_az == None or type(self._deg_az) != int:
      raise ValueError('Steps per degree in azimuth must be an integer!')
    if self._deg_el == None or type(self._deg_el) != int:
      raise ValueError('Steps per degree in elevation must be an integer!')
    
    
  def configure_limit_switch_INT(self):
    self.logger.info('Initializing rising edge INT on pin [{}, {}]'.format(self._lim_az, self._el))

    # set up rising edge detectors for each pin
    #GPIO.add_event_detect(self._lim_az, GPIO.RISING, callback=self.__ISR_lim_az)
    #GPIO.add_event_detect(self._lim_el, GPIO.RISING, callback=self.__ISR_lim_el)


  #def __ISR_lim_az(self, pin):
  #
  #def __ISR_lim_el(self, pin):
  
    
  #TODO: Pass parameters using enum
  def move_motor(self, axis, dir, deg):
    if not isinstance(dir, MotorCtrl_t):
      raise ValueError('Direction is not of direction type enumerate')

    # decode direction enum due to weird states when the enum members aren't unique.
    # during testing when multiple members were the same integer value caused
    # names to get mixed up between az/el. Fine for driving motors, but logging and UI
    # would become very confusing.
    mot_dir = -1 # induce error if we somehow don't update
    if dir == MotorCtrl_t.IDLE:
      self.logger.debug('Motor is in IDLE mode, not moving')
      return
    elif dir == MotorCtrl_t.WEST:
      mot_dir = 0
    elif  dir == MotorCtrl_t.NORTH:
      mot_dir = 0
    elif dir == MotorCtrl_t.EAST:
      mot_dir = 1
    elif dir == MotorCtrl_t.SOUTH:
      mot_dir = 1
    
    if axis == self._az:
      steps = deg * self._deg_az
      self.logger.debug('Moving azimuth {} degrees which is ~{} steps'.format(deg, steps))
    elif axis == self._el:
      steps = deg * self._deg_el
      self.logger.debug('Moving elevation {} degrees which is ~{} steps'.format(deg, steps))
    else:
      self.logger.error('Incorrect axis! Expected {} or {}, you passed {}'.format(self._az, self._el, axis))
      return
      
    self.logger.debug('Move motor routine commencing')
    MOT.output(self._clk, self._ENABLE) #sets clock pin high, falling edge
    MOT.output(self._dir, mot_dir)  #sets motor direction 0 = W/N, 1 = E/S
    MOT.output(axis, self._DISABLE)    
    MOT.output(self._rst, 1)        #resets to starting configuration 1010
    MOT.output(self._rst, 0)        #starts reset
    MOT.output(self._rst, 1)        #ends reset
    MOT.output(axis, self._ENABLE)
      
    self.logger.debug('Pulsing clock {} times'.format(steps))
    for _ in range(int(steps)): #pulse the clock pin
      MOT.output(self._clk, self._DISABLE)
      time.sleep(self._speed)
      MOT.output(self._clk, self._ENABLE)
      time.sleep(self._speed)
    
    self.logger.debug('Motor move finished. Disabling specified axis motor')
    MOT.output(axis, self._DISABLE)
