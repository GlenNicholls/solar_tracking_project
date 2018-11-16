import time
import logging
import RPi.GPIO as MOT
from enum import Enum, unique

#TODO: Define a constants file???
#Constants
# WEST = 0
# NORTH = 0
# EAST = 1
# SOUTH = 1
# ENABLE = 1
# DISABLE = 0
class MotorCtrl_t(Enum):
    WEST    = 0
    NORTH   = 0
    EAST    = 1
    SOUTH   = 1
    ENABLE  = 1
    DISABLE = 0


class stepper_motor(object):

  def __init__(self, logger_name        = 'main_logger', 
                     logger_module_name = 'stepper_motor',
                     pin_elevation      = None,
                     pin_azimuth        = None,
                     pin_direction      = None,
                     pin_clock          = None,
                     pin_reset          = None,
                     az_steps_per_deg   = None,
                     el_steps_per_deg   = None
               ):
    # instantiate logger
    self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
    self.logger.info('creating an instance of the {}'.format(logger_module_name))

    self._speed = 0.001

    # define pin numbers
    self._dir = pin_direction
    self._el  = pin_elevation
    self._clk = pin_clock
    self._az  = pin_azimuth
    self._rst = pin_reset
    
    self._pin_t = (self._dir, self._el, self._clk, self._az, self._rst)
    
    if len(self._pin_t) > len(set(self._pin_t)):
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
    
    
    #MOT.setmode(MOT.BCM)
    #lines = [DIR, EL, CLK, AZ, RST] # TODO: Make this part of class init
    #for pin in lines:  #sets pins 12,13,16,19,26 as outputs
    #    MOT.setup(pin,MOT.OUT) # TODO: should be done in main
  
    
  #TODO: Pass parameters using enum
  def move_motor(self, axis, dir, deg):
    if not isinstance(dir, MotorCtrl_t):
      raise ValueError('Direction is not of direction type enumerate')

    if axis == self._az:
      steps = deg * self._deg_az
      self.logger.debug('Moving azimuth {} degrees which is {} steps'.format(deg, steps))
    elif axis == self._el:
      steps = deg * self._deg_el
      self.logger.debug('Moving elevation {} degrees which is {} steps'.format(deg, steps))
    else:
      self.logger.error('Incorrect axis! Expected {} or {}, you passed {}'.format(self._az, self._el, axis))
      return
      
    self.logger.debug('Move motor routine commencing')
    MOT.output(self._clk, MotorCtrl_t.ENABLE)  #sets clock pin high, falling edge
    MOT.output(self._dir, dir)     #sets motor direction 1 = W/N, 0 = E/S
    MOT.output(axis, MotorCtrl_t.DISABLE)
    MOT.output(self._rst, 1)       #resets to starting configuration 1010
    MOT.output(self._rst, 0)       #starts reset
    MOT.output(self._rst, 1)       #ends reset
    MOT.output(axis, MotorCtrl_t.ENABLE)
      
    self.logger.debug('Pulsing clock {} times'.format(steps))
    for _ in range(steps): #pulse the clock pin
      MOT.output(self._clk, MotorCtrl_t.DISABLE)
      time.sleep(self._speed)
      MOT.output(self._clk, MotorCtrl_t.ENABLE)
      time.sleep(self._speed)
    
    self.logger.debug('Motor move finished. Disabling specified axis motor')
    MOT.output(axis, DISABLE)
  #End move_motor
  
#End stepper_motor
