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
    self.logger.info('creating an instance of the ' + __name__ + ' with the alias {}'.format(logger_module_name))

    # global variables
    self._speed   = 0.001 # hardcoding here as don't want sys to unintentionally become unstable
    self._ENABLE  = 1
    self._DISABLE = 0
    self._INT_az  = False
    self._INT_el  = False

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
    self.logger.info('Initializing logic change INT on pin [{}, {}]'.format(self._lim_az, self._lim_el))

    # set up logic change detectors for each pin
    MOT.add_event_detect(self._lim_az, MOT.RISING, callback=self.__ISR_lim_az)
    MOT.add_event_detect(self._lim_el, MOT.RISING, callback=self.__ISR_lim_el)


  def __ISR_lim_az(self, pin):
    #if MOT.input(pin):
    self._INT_az = True
  

  def __ISR_lim_el(self, pin):
    #if MOT.input(pin):
    self._INT_el = True
  
    
  def __motor_step(self):
    MOT.output(self._clk, self._DISABLE)
    time.sleep(self._speed)
    MOT.output(self._clk, self._ENABLE)
    time.sleep(self._speed)

    
  def __move_motor_until_lim(self):
    while not self._INT_az and not self._INT_el:
      self.__motor_step()
    return self._INT_az or self._INT_el
      


  def __move_motor_x_steps(self, steps):
    step_cnt = 0
    lim_reached = False
    for i in range(int(round(steps))):
      step_cnt = i
      self.__motor_step()

      # break if we see we have hit lim switches
      if self._INT_az:
        lim_reached = True
        self.logger.warn('Azimuth limit reached, stepping motor back to safe limit!!!')
        break
      if self._INT_el:
        lim_reached = True
        self.logger.warn('Elevation limit reached, stepping motor back to safe limit!!!')
        break
    self.logger.debug('Moved motor {} steps'.format(step_cnt+1)) # i starts at zero and goes to x-1
    return lim_reached


  def __activate_mot_move(self, pin, direction):
    MOT.output(self._clk, self._ENABLE) #sets clock pin high, falling edge
    MOT.output(self._dir, direction)    #sets motor direction 0 = W/N, 1 = E/S
    MOT.output(pin, self._DISABLE)    
    MOT.output(self._rst, self._ENABLE) #resets to starting configuration 1010
    MOT.output(self._rst, self._ENABLE) #starts reset
    MOT.output(self._rst, self._ENABLE) #ends reset
    MOT.output(pin, self._ENABLE)


  def move_motor(self, axis, dir, deg, cal=False):
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
    
    if mot_dir:
      mot_dir_N = 0
    else:
      mot_dir_N = 1
      
    # calculate num of steps for each axis
    if axis == self._az:
      steps = abs(deg) * self._deg_az
      self.logger.debug('Moving azimuth {} degrees which is ~{} steps'.format(deg, steps))
    elif axis == self._el:
      steps = abs(deg) * self._deg_el
      self.logger.debug('Moving elevation {} degrees which is ~{} steps'.format(deg, steps))
    else:
      self.logger.error('Incorrect axis! Expected {} or {}, you passed {}'.format(self._az, self._el, axis))
      return
      
    # activate motor for desired direction
    self.logger.debug('Move motor routine commencing')
    self.__activate_mot_move(axis, mot_dir)

    # step moter desired num of steps
    if cal:
      self.logger.info('Beginning calibration routine')
      lim_reached = self.__move_motor_until_lim()
    else:
      self.logger.debug('Moving motor {} steps'.format(steps))
      lim_reached = self.__move_motor_x_steps(steps)
    
    # if we hit limit switches, step backwards until safe
    if lim_reached:
      self.__activate_mot_move(axis, mot_dir_N)
      while MOT.input(self._lim_az) or MOT.input(self._lim_el):
        self.__motor_step()
      self._INT_az = False
      self._INT_el = False
      self.logger.info('Motor has been repositioned to safe limit!!')

    self.logger.debug('Motor move finished. Disabling specified axis motor')
    MOT.output(axis, self._DISABLE)
    return lim_reached
