from __future__ import division
import logging
import RPi.GPIO as GPIO  
from utils import hardware as HW

class encoder:

  def __init__(self, logger_name        = 'main_logger',
                     logger_module_name = 'shaft_encoder',
                     a_pin              = None,
                     b_pin              = None,
                     init_count         = 0, 
                     ppr                = 0
                ):
    # instantiate logger
    self.logger = logging.getLogger(logger_name + '.' + logger_module_name)
    self.logger.info('creating an instance of the ' + __name__ + ' with the alias {}'.format(logger_module_name))
    
    # Define pin numbers for A/B channels on azimuth/elevation motors
    self.A_pin=a_pin
    self.B_pin=b_pin

    if len((self.A_pin, self.B_pin)) > len(set((self.A_pin, self.B_pin))):
      raise ValueError('GPIO pin numbers must be unique integers!')
    if self.A_pin == None or type(self.A_pin) != int:
      raise ValueError('GPIO must be an integer!')
    else:
      self.logger.debug('Shaft encoder A pin: {}'.format(self.A_pin))
    if self.B_pin == None or type(self.B_pin) != int:
      raise ValueError('GPIO Must be integer!')
    else:
      self.logger.debug('Shaft encoder B pin: {}'.format(self.B_pin))

    # Define pulses per revolution (2000 for chosen encoders)
    self.ppr = ppr

    if type(self.ppr) != int or self.ppr == 0:
      raise ValueError('Pulse per revolution Must be integer >0!')
    else:
      self.logger.debug('Shaft encoder PPR: {}'.format(self.ppr))
    
    # Define global count variables
    self.a_count = init_count

    if type(self.a_count) != int or self.a_count < 0 or self.a_count > self.ppr:
      raise ValueError('Initial count value must be integer 0-ppr')


  def configure_encoder_INT(self):
    self.logger.info('Initializing rising edge INT on pin {}'.format(self.A_pin))             

    # Set up rising edge detectors for each pin
    GPIO.add_event_detect(self.A_pin, GPIO.RISING, callback=self.__ISR_pin_a)


  # A channel ISR
  def __ISR_pin_a(self, pin):
    # Check if channel A is leading channel B (A=1,B=0)
    # If channel A leads, rotation is CCW
    # Increment/Decrement position counter based on direction
    print GPIO
    print GPIO.input(self.B_pin)    
    print GPIO.input(self.A_pin)

    if GPIO.input(self.B_pin):
      #CCW
      self.a_count += 1
    else:
      #CW
      self.a_count -= 1


  def get_degrees(self):
    deg = self.a_count * 360.0 / self.ppr
    self.logger.debug('Shaft encoder degrees: {}'.format(deg))
    return deg
  

  def get_count(self):
    self.logger.debug('Shaft encoder count: {}'.format(self.a_count))
    return self.a_count


  def set_count(self, SE_count):
    self.logger.info('Setting encoder current count value to: {}'.format(SE_count))
    self.a_count = SE_count


  def set_degrees(self, deg):
    self.logger.info('Setting encoder current position value to: {} deg'.format(deg))
    cnt = int(round(self.ppr * deg / 360.0)) # round to nearest integer and typecast from float to int
    self.set_count(cnt)
