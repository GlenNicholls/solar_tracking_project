#!/usr/bin/env python

import sys
import time
import logging
import argparse

from datetime import datetime, timedelta
from astral import Astral, Location
import pytz
import os

# i know this is terrible practice, but the documentation
# isn't the greatest
from consolemenu import *       
from consolemenu.format import *
from consolemenu.items import * 

import RPi.GPIO as GPIO
from Adafruit_MCP3008.MCP3008 import MCP3008

from sun_sensor        import sun_sensor
from utils             import utils, hardware
from DS3231            import DS3231
from motor_control     import stepper_motor, MotorCtrl_t
from shaft_encoder     import encoder
from system_monitor    import system_monitor
from power_measurement import power_measurement


#NOTE: indentation is 2 spaces
  
# TODO: Need to set up pi to add this main.py routine to startup -GN
# TODO: Need to find way to save state for periodically shutting down -GN

##########################
# GPIO Pin Definitions
##########################
# NOTE: Using BCM pin numbering for all
# Shaft Encoders
PIN_SE_AZIMUTH_A   = 26  
PIN_SE_AZIMUTH_B   = 13 
PIN_SE_ELEVATION_A = 11 
PIN_SE_ELEVATION_B = 5 

# ADC
PIN_ADC_CLK  = 21 
PIN_ADC_MISO = 19 
PIN_ADC_MOSI = 20 
PIN_ADC_CS   = 10 

# RTC is accounted for based on I2C channel

# ATTiny
# NOTE: Program pins accounted for in Makefile
PIN_UC_PWR_ACK_TX  = 25 
PIN_UC_FAULT_RX    = 7  
PIN_UC_DEV_MODE_RX = 8  

# Motor Control
PIN_MOT_AZIMUTH   = 22
PIN_MOT_ELEVATION = 27
PIN_MOT_RESET     = 6
PIN_MOT_CLOCK     = 9
PIN_MOT_DIRECTION = 1

# Limit switches
PIN_LIM_SW_AZIMUTH   = 18
PIN_LIM_SW_ELEVATION = 17


##########################
# instantiate sub-modules
##########################
# User location
thismodule = sys.modules[__name__]
thismodule.latitude  = 38.893950
thismodule.longitude = -104.800898
thismodule.elevation = 6000

# Logger
logger_name = 'main_app'
logger_rtc_name         = 'rtc'
logger_sys_mon_name     = 'sys_mon'
logger_panel_pwr_name   = 'panel_power'
logger_az_encoder_name  = 'azimuth_encoder'
logger_el_encoder_name  = 'elevation_encoder'
logger_battery_pwr_name = 'battery_power'
logger_sun_sensor_name  = 'sun_sensor'
logger_motor_name       = 'motor'
logger_hw_name          = 'hardware_info'

util_handle = utils(logger_name)
logger = util_handle.init_logger()

# RTC
i2c_port  = 1 # set to 0 if using gen 1 pi
i2c_addr  = 0x68

rtc = DS3231( logger_name        = logger_name,
              logger_module_name = logger_rtc_name,
              i2c_port           = i2c_port,
              i2c_addr           = i2c_addr,
              latitude           = thismodule.latitude,
              longitude          = thismodule.longitude
             )

# System Monitor
sys_mon = system_monitor( logger_name        = logger_name,
                          logger_module_name = logger_sys_mon_name
                         )

# ADC
adc_vref     = 3.3
adc_num_bits = 10

adc_ch_panel_current   = 0
adc_ch_battery_current = 1
adc_ch_battery_voltage = 2
adc_ch_panel_voltage   = 3
adc_ch_south_sun_sens  = 4 
adc_ch_west_sun_sens   = 5 
adc_ch_north_sun_sens  = 6 
adc_ch_east_sun_sens   = 7 

adc = MCP3008( clk  = PIN_ADC_CLK,
               cs   = PIN_ADC_CS,
               miso = PIN_ADC_MISO,
               mosi = PIN_ADC_MOSI
              )

# Power Measurements
curr_sens_gain = 75

curr_sens_panel_Rshunt = 0.010
vdiv_panel_R1          = 100e3
vdiv_panel_R2          = 16e3

curr_sens_battery_Rshunt = 0.001
vdiv_battery_R1          = 100e3
vdiv_battery_R2          = 36e3

panel_power = power_measurement( logger_name          = logger_name,
                                 logger_module_name   = logger_panel_pwr_name,
                                 adc_volt_ref         = adc_vref,
                                 adc_num_bits         = adc_num_bits,
                                 adc_current_channel  = adc_ch_panel_current,
                                 adc_voltage_channel  = adc_ch_panel_voltage,
                                 adc_object           = adc,
                                 current_amp_gain     = curr_sens_gain,
                                 current_amp_Rshunt   = curr_sens_panel_Rshunt,
                                 vdiv_R1              = vdiv_panel_R1,
                                 vdiv_R2              = vdiv_panel_R2
                                )

battery_power = power_measurement( logger_name          = logger_name,
                                   logger_module_name   = logger_battery_pwr_name,
                                   adc_volt_ref         = adc_vref,
                                   adc_num_bits         = adc_num_bits,
                                   adc_current_channel  = adc_ch_battery_current,
                                   adc_voltage_channel  = adc_ch_battery_voltage,
                                   adc_object           = adc,
                                   current_amp_gain     = curr_sens_gain,
                                   current_amp_Rshunt   = curr_sens_battery_Rshunt,
                                   vdiv_R1              = vdiv_battery_R1,
                                   vdiv_R2              = vdiv_battery_R2
                                  )

# Sun Sensor
mot_move_raw_thresh = 20
sun_sensors = sun_sensor( logger_name         = logger_name,
                          logger_module_name  = logger_sun_sensor_name,
                          mot_move_raw_thresh = mot_move_raw_thresh,
                          adc_volt_ref        = adc_vref,
                          adc_north_sens_ch   = adc_ch_north_sun_sens,
                          adc_east_sens_ch    = adc_ch_east_sun_sens,
                          adc_south_sens_ch   = adc_ch_south_sun_sens,
                          adc_west_sens_ch    = adc_ch_west_sun_sens,
                          adc_object          = adc
                         )

# Shaft Encoders
SE_ppr = 2000
az_encoder = encoder( logger_name        = logger_name,
                      logger_module_name = logger_az_encoder_name,
                      a_pin              = PIN_SE_AZIMUTH_A,
                      b_pin              = PIN_SE_AZIMUTH_B,
                      init_count         = 0, # TODO: load from file
                      ppr                = SE_ppr
                     )

el_encoder = encoder( logger_name        = logger_name,
                      logger_module_name = logger_el_encoder_name,
                      a_pin              = PIN_SE_ELEVATION_A,
                      b_pin              = PIN_SE_ELEVATION_B,
                      init_count         = 0, # TODO: load from file
                      ppr                = SE_ppr
                     )

# Motors
az_steps_per_deg = 50
el_steps_per_deg = 62
motor = stepper_motor( logger_name          = logger_name,
                       logger_module_name   = logger_motor_name,
                       pin_elevation        = PIN_MOT_ELEVATION,
                       pin_azimuth          = PIN_MOT_AZIMUTH,
                       pin_direction        = PIN_MOT_DIRECTION,
                       pin_clock            = PIN_MOT_CLOCK,
                       pin_reset            = PIN_MOT_RESET,
                       pin_lim_sw_azimuth   = PIN_LIM_SW_AZIMUTH,
                       pin_lim_sw_elevation = PIN_LIM_SW_ELEVATION,
                       az_steps_per_deg     = az_steps_per_deg,
                       el_steps_per_deg     = el_steps_per_deg
                      )

# HAL
hw_handle = hardware( logger_name        = logger_name,
                      logger_module_name = logger_hw_name
                     )


##########################
# init packages
##########################
def init_pins():
  # debug
  logger.info('Cleaning up all GPIO')
  GPIO.cleanup()
  
  logger.info('Setting GPIO pin warnings to true')
  GPIO.setwarnings(True)

  # mode
  logger.info('Setting GPIO pin mode to BCM')
  GPIO.setmode(GPIO.BCM)
  
  # SE  
  logger.info('Setting GPIO pin directions for shaft encoder')

  GPIO.setup(PIN_SE_AZIMUTH_A,   GPIO.IN)
  GPIO.setup(PIN_SE_AZIMUTH_B,   GPIO.IN)
  GPIO.setup(PIN_SE_ELEVATION_A, GPIO.IN)
  GPIO.setup(PIN_SE_ELEVATION_B, GPIO.IN)

  # ADC taken care of by Adafruit_MCP3008

  # ATTiny
  logger.info('Setting GPIO pin directions for ATTiny control')

  GPIO.setup(PIN_UC_PWR_ACK_TX,  GPIO.OUT)
  GPIO.setup(PIN_UC_FAULT_RX,    GPIO.IN)
  GPIO.setup(PIN_UC_DEV_MODE_RX, GPIO.IN)

  # Motors
  logger.info('Setting GPIO pin directions for motor control driver L297')
  GPIO.setup(PIN_MOT_AZIMUTH,   GPIO.OUT)
  #usr_ready = raw_input('Are you ready to open the menu interface? Press [ENTER] to continue')

  GPIO.setup(PIN_MOT_ELEVATION, GPIO.OUT) # BUG: this is causing motor to lock up!!!
  #usr_ready = raw_input('Are you ready to open the menu interface? Press [ENTER] to continue')
  GPIO.setup(PIN_MOT_RESET,     GPIO.OUT)
  GPIO.setup(PIN_MOT_CLOCK,     GPIO.OUT)
  GPIO.setup(PIN_MOT_DIRECTION, GPIO.OUT)  
  
  # Limit Switches
  logger.info('Setting GPIO pin directions for limit switches')
  
  GPIO.setup(PIN_LIM_SW_AZIMUTH,   GPIO.IN)
  GPIO.setup(PIN_LIM_SW_ELEVATION, GPIO.IN)


def init_pi_hat():
  logger.info('Setting Pi Hat ACK high')
  hw_handle.set_pin_high(PIN_UC_PWR_ACK_TX)

  logger.info('Checking Pi Hat FAULT')
  if hw_handle.pin_is_set(PIN_UC_FAULT_RX):
    logger.error('Pi Hat power circuit FAULT! Check circuit and functionality before clearing condition!')
    # TODO: email user or something


def init_interrupts():
  az_encoder.configure_encoder_INT()
  el_encoder.configure_encoder_INT()
  motor.configure_limit_switch_INT()


def init_rtc():
  # Checking RTC alarms
  rtc.check_and_clear_alarms()

  # Initial checks for time accuracy
  rtc_now, local_now, delta = rtc.get_datetime_delta(return_all=True)

  # config rtc
  if delta.days > 0:
    logger.info('RTC is off by [{}] days, re-configuring device'.format(delta.days))
    rtc.configure_rtc()

  # update RTC if power was lost or if we have internet connection
  if rtc.get_power_lost():
    logger.error('RTC Power was lost. Check the battery of the system and for the RTC!')
  else:
    logger.info('RTC power was not lost, system healthy.')

  if delta.seconds > 2.0:
    logger.info('RTC time is not accurate, attempting to re-adjust')

    if sys_mon.is_wlan_connected():
      logger.info('There is an internet connection, adjusting RTC time')
      rtc.set_datetime_now()
    else:
      logger.error('No internet connection, unable to adjust RTC time!')
  else:
    logger.info('RTC time is accurate, skipping adjustment routine')



##########################
# Helpers
##########################
# TODO: where should these go??
def get_encoder_positions_deg():
  logger.info('Get current position from shaft encoders')
  az_deg = az_encoder.get_degrees()
  el_deg = el_encoder.get_degrees()
  logger.info('Shaft encoder azimuth: [{}] deg'.format(az_deg))
  logger.info('Shaft encoder elevation: [{}] deg'.format(el_deg))
  return az_deg, el_deg


def get_location_astral(lat, lng, elev):
  loc = Location()
  loc.name = 'solar_tracker'
  loc.region = 'whereIam'
  loc.latitude = lat
  loc.longitude = lng
  loc.timezone = 'US/Mountain'
  loc.elevation = elev # TODO: do we need this?
  logger.info('Astral location: [{}]'.format(loc))
  return loc


def get_solar_position_deg(loc_astral):
  az_deg = loc_astral.solar_azimuth(datetime.now())
  el_deg = loc_astral.solar_elevation(datetime.now())
  logger.info('Next Solar Azimuth: [{}] deg'.format(az_deg))
  logger.info('Next solar elevation: [{}] deg'.format(el_deg))
  return az_deg, el_deg


def get_sunrise_position_deg(loc_astral):
  tomorrow = datetime.today() + timedelta(days=1)
  sun_dict = loc_astral.sun(tomorrow.date())
  az_deg = loc_astral.solar_azimuth(sun_dict['sunrise'])
  el_deg = loc_astral.solar_elevation(sun_dict['sunrise'])
  logger.info('Sunrise azimuth tomorrow: [{}] deg'.format(az_deg))
  logger.info('Sunrise elevation tomorrow: [{}] deg'.format(el_deg))
  return az_deg, el_deg


def get_motors_dir_open_loop(deg_az, deg_el):
  if deg_az < 0:
    dir_az = MotorCtrl_t.EAST
  else:
    dir_az = MotorCtrl_t.WEST
  
  if deg_el < 0:
    dir_el = MotorCtrl_t.SOUTH
  else:
    dir_el = MotorCtrl_t.NORTH
  return dir_az, dir_el


def move_motor_az(direction, degrees):
  logger.info('Moving azimuth [{}] degrees [{}]'.format(degrees, direction))
  lim_reached = motor.move_motor(PIN_MOT_AZIMUTH, direction, degrees)
  return lim_reached


def move_motor_el(direction, degrees):
  logger.info('Moving elevation [{}] degrees [{}]'.format(degrees, direction))
  lim_reached = motor.move_motor(PIN_MOT_ELEVATION, direction, degrees)
  return lim_reached


# TODO: adding actual feedback loop with PI or PID might be cleaner
def move_motors_open_loop(deg_az, deg_el, skip_az=False, skip_el=False):
  locked = False
  locked_az = skip_az
  locked_el = skip_el
  enc_thresh = 0.25 # defining tight threshold for motors

  # create constant to generate error term later without multiplier
  desired_deg_az = deg_az
  desired_deg_el = deg_el

  # if encoders aren't reading correct position, loop
  not_lock_cnt = 0
  while not locked and not_lock_cnt < 10:
    # get previous position from encoders
    prev_deg_az, prev_deg_el = get_encoder_positions_deg()

    # get directions for motors
    dir_az, dir_el = get_motors_dir_open_loop(deg_az, deg_el)

    # move motors
    if not locked_az:
        move_motor_az(dir_az, deg_az)
    if not locked_el:
        move_motor_el(dir_el, deg_el)

    # update position for lock check
    new_deg_az, new_deg_el = get_encoder_positions_deg()

    enc_moved_deg_az = new_deg_az - prev_deg_az
    enc_moved_deg_el = new_deg_el - prev_deg_el
    logger.info('Azimuth shaft encoder degrees moved: [{}]'.format(enc_moved_deg_az))
    logger.info('Elevation shaft encoder degrees moved: [{}]'.format(enc_moved_deg_el))

    # check if locked
    #deg_az = abs(new_deg_az - desired_deg_az)
    #deg_el = abs(new_deg_el - desired_deg_el)
    deg_az = desired_deg_az - new_deg_az
    deg_el = desired_deg_el - new_deg_el 
    err_deg_az = abs(deg_az)
    err_deg_el = abs(deg_el)
    if err_deg_az <= enc_thresh and not locked_az:
      logger.info('Azimuth Locked!!!')
      locked_az = True
    elif not locked_az:
      logger.warn('Desired Azimuth: [{}] deg'.format(desired_deg_az))
      logger.warn('Current Azimuth: [{}] deg'.format(new_deg_az))
      logger.warn('Azimuth error: [{}] deg'.format(err_deg_az))

    if err_deg_el <= enc_thresh and not locked_el:
      logger.info('Elevation Locked!!!')
      locked_el = True
    elif not locked_el:
      logger.warn('Desired Elevation: [{}] deg'.format(desired_deg_el))
      logger.warn('Current Elevation: [{}] deg'.format(new_deg_el))
      logger.warn('Elevation error: [{}] deg'.format(err_deg_el))

    if locked_az and locked_el:
      logger.info('Azimuth and elevation are locked!!!')
      locked = True
    
    # increment not locked counter
    not_lock_cnt += 1

  if not locked:
    logger.error('Unable to reach correct azimuth and elevation positions!!!')

  logger.info('Azimuth shaft encoder final: [{}]'.format(new_deg_az))
  logger.info('Elevation shaft encoder final: [{}]'.format(new_deg_el))
  return locked
  

def move_motors_closed_loop():
  locked = False
  move_mot_deg = 0.5

  not_lock_cnt = 0
  while not locked and not_lock_cnt < 10:
    # get motor movement directions based on sun sensor
    az_dir, el_dir = sun_sensors.get_motor_direction_all()
    logger.info('Desired azimuth direction: [{}]'.format(az_dir))
    logger.info('Desired elevation direction: [{}]'.format(el_dir))

    # move motors
    move_motor_el(el_dir, move_mot_deg)
    move_motor_az(az_dir, move_mot_deg)

    # check if locked
    if az_dir == MotorCtrl_t.IDLE:
      logger.info('Azimuth Locked!!!')
    if el_dir == MotorCtrl_t.IDLE:
      logger.info('Elevation Locked!!!')
    if az_dir == MotorCtrl_t.IDLE and el_dir == MotorCtrl_t.IDLE:
      logger.info('Azimuth and elevation are locked!!!')
      locked = True

    # increment not locked counter
    not_lock_cnt + 1

  if not locked:
    logger.error('Unable to reach correct azimuth and elevation positions!!!')

  return locked


def move_motors(deg_az=None, deg_el=None, open_loop=False, closed_loop=False, skip_az=False, skip_el=False):
  if open_loop and closed_loop:
    raise ValueError('Must select open loop OR closed loop, not both!')
  if open_loop and (deg_az == None or deg_el == None):
    raise ValueError('Must enter movement values for BOTH azimuth and elevation')
  if closed_loop and (deg_az != None or deg_el != None):
    self.logger.warn('Ignoring program calculated azimuth and elevation degree movements in closed loop mode!')

  if open_loop:
    logger.info('Open loop tracking initiated')
    move_motors_open_loop(deg_az, deg_el, skip_az, skip_el)
  elif closed_loop:
    logger.info('Closed loop tracking initiated')
    move_motors_closed_loop()


def is_daytime(loc_astral):
  #now = datetime.now()
  now = pytz.timezone('US/Mountain').localize(datetime.now())
  sun_dict = loc_astral.sun()
  if now > sun_dict['sunrise'] and now < sun_dict['sunset']:
    logger.info("Daytime")
    return True
  else:
    logger.info("Nighttime")
    return False


def calibrate_az():
  logger.info('Calibrating Azimuth')
  lim = False
  fail_cnt = 0

  while not lim:
    # get previous position
    prev, _ = get_encoder_positions_deg()

    # move motor
    lim = move_motor_az(MotorCtrl_t.EAST, 0.5)

    # get new position
    new, _ = get_encoder_positions_deg()

    # error check movement
    if abs(prev - new) < 0.2:
      fail_cnt += 1
    if fail_cnt > 5:
      logger.critical('Motors not moving, calibration FAILED!!!')
      break

  az_encoder.set_degrees(55.0)


def calibrate_el():
  logger.info('Calibrating Elevation')
  lim = False
  fail_cnt = 0

  while not lim:
    # get previous position
    _, prev = get_encoder_positions_deg()

    # move motor
    lim = move_motor_el(MotorCtrl_t.SOUTH, 0.5)

    # get new position
    _, new = get_encoder_positions_deg()

    # error check movement
    if abs(prev - new) < 0.2:
      fail_cnt += 1
    if fail_cnt > 5:
      logger.critical('Motors not moving, calibration FAILED!!!')
      break

  el_encoder.set_degrees(0)


def calibrate_motors():
  logger.info('Starting system calibration')
  calibrate_az()
  calibrate_el()


'''
todo: list for uC stuff -GN
x 1) startup should drive uC ack pin high
2) FAULT pin should be an interrupt. If this ever goes high, need to somehow
   issue text/email/tweet notifying user that uC has experienced an issue
4) once dev mode pin from uC is low, then drive ack pin to uC low and commence
   >>> shutdown -h now immediately
5) will think about other cases that need to be accounted for in here
'''
# TODO: determine how time will be passed in for update alarm and the error checking for this value
def shutdown(shutdown_until_sunrise=False, shutdown_until_update=False):
  # TODO: add flag for nighttime and add this to rtc.set_alarm_sunrise() check
  logger.info('Initiating Shutdown')

  # TODO: logic below
  '''
  # if we want to power down between update periods do this, else set alarm for sunrise
  if (periodic sleep during tracking is desired):
    # TODO: change name to set_alarm_delta() as this name seems dumb now that I read it again
    rtc.set_alarm_now_delta(minutes=?, seconds=?) # values propagated down and calculation done based on user update deg frequency
  else:
    rtc.set_alarm_sunrise()
  hw_handle.set_pin_low(PIN_UC_PWR_ACK_TX) #uC will now wait ~45 seconds to pull power
  os.system('sudo shutdown now -h')
  '''
# TODO: Add functions below
# def calibrate_system():
# def load_stored_parameters():
# def load_user_parameters():
# def save_state():


##########################
# Menus
##########################  
def menu_normal_op():
  # Load stored parameters
  logger.warn('Loading stored prarmeters NOT DEFINED')
  
  #Load user specifice parameters
  logger.warn('Loading user specified parameters NOT DEFINED')
  
  #Get astral with current location
  loc_astral = get_location_astral(thismodule.latitude, thismodule.longitude, thismodule.elevation)
  
  # Calibrate system
  logger.warn('Calibrating System NOT DEFINED')
     
  # infinite loop
  while True:
      open_loop_locked   = False
      closed_loop_locked = False
      if is_daytime(loc_astral): #this will be the if check from above, implemented this way for development
        # get encoder current positions
        prev_enc_az = az_encoder.get_degrees()
        prev_enc_el = el_encoder.get_degrees()

        # Get solar position
        solar_deg_az, solar_deg_el = get_solar_position_deg(loc_astral)
        
        # Move to calculated sun posistion
        deg_az = solar_deg_az - prev_enc_az
        deg_el = solar_deg_el - prev_enc_el 
        if deg_az > 1.0 or deg_el > 1.0:
          open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)
        
          # Perform fine adjustments
          closed_loop_locked = move_motors(closed_loop=True)

        # check for lock state
        if not closed_loop_locked or not open_loop_locked:
          logger.warn('Unable to acquire sun lock in open or closed loop algorithms')

        #Read light sensor
        # TODO: is this referring to limit switch? If so, I am taking care of this in motor class -GN
        logger.info('Reading light sensor')
        
      else:
        # get current encoder positions
        prev_enc_az = az_encoder.get_degrees()
        prev_enc_el = el_encoder.get_degrees()

        # get solar position for tomorrow morning
        solar_deg_az, solar_deg_el = get_sunrise_position_deg(loc_astral)
        
        # Move to sunrise position for tomorrow
        logger.info('Moving to sunrise position for tomorrow')
        
        deg_az = solar_deg_az - prev_enc_az
        deg_el = solar_deg_el - prev_enc_el 
        open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)

      logger.warn('Sleep calculation NOT DEFINED, defaulting sleep to 30s in loop')
      time.sleep(30)
  # end infinite loop
  # TODO: log to dataframe and dump to file before shutting down
  logger.warn('Log system information NOT DEFINED')

  # TODO: use GPIO.cleanup() or GPIO.cleanup([channels]) somewhere before shutdown.
  #       cleanup() may cause issues with AVRDude, so specifying used channels as [] or () is probably needed
  # TODO: check pin_is_set(PIN_UC_DEV_MODE_RX) to determine if we will use time.sleep() for the desired amount of time
  #       or if we can actually shutdown and set an alarm. If true, must operate inside a while True: loop and send email to user 
  #       if they forget to take the device out of dev mode after an hour or something.
  # TODO: measure power of shutdown/power up to see if it is worth it during day. If it is, make sure we aren't shutting down if next alarm will be
  #       before amount of time it takes to shutdown


def menu_open_loop():
  logger.info('Open loop tracking menu selected')

  prev_enc_az = az_encoder.get_degrees()
  prev_enc_el = el_encoder.get_degrees()
  
  #Get astral with current location
  loc_astral = get_location_astral(thismodule.latitude, thismodule.longitude, thismodule.elevation)
  
  if is_daytime(loc_astral): #this will be the if check from above, implemented this way for development
    # Get solar position
    solar_deg_az, solar_deg_el = get_solar_position_deg(loc_astral)
    
    # Move to calculated sun posistion
    deg_az = solar_deg_az - prev_enc_az
    deg_el = solar_deg_el - prev_enc_el 
    open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)
  else:
    #Get solar position for tomorrow morning
    solar_deg_az, solar_deg_el = get_sunrise_position_deg(loc_astral)
    
    # Move to sunrise position for tomorrow
    logger.info('Moving to sunrise position for tomorrow')
    
    deg_az = solar_deg_az - prev_enc_az
    deg_el = solar_deg_el - prev_enc_el 
    open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)

  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_sun_simulation():
  logger.info('Open loop sun simulation menu selected')
  
  while True:
    # Show user current positions
    get_encoder_positions_deg()

    # Get solar position from user
    print('Enter the next sun location or type \'q\' to quit')
    user_az = raw_input('Enter azimuth sun position in degrees:')
    user_el = raw_input('Enter elevation sun position in degrees:')

    if user_az.lower() == 'q' or user_el.lower() == 'q':
      break
    else:
      deg_az = float(user_az)
      deg_el = float(user_el)
    
    # Move to calculated sun posistion
    open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)

  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_closed_loop():
  logger.info('Closed loop tracking menu selected')
  closed_loop_locked = move_motors(closed_loop=True)
  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')
    

def menu_set_az_position():
  logger.info('Set azimuth position menu selected')
  get_encoder_positions_deg()
  while True:
    deg = raw_input('Enter desired azimuth position in degrees or \'q\' to quit:')
    if deg == 'q' or deg == 'Q':
      break
    else:
      if float(deg) > 55.5:
        logger.info('Setting azimuth position to: [{}] deg'.format(deg))
        move_x_deg = float(deg) - curr_az
        move_motors(deg_az=float(move_x_deg), deg_el=0.0, open_loop=True, skip_el=True)
        break
      else:
        logger.error('Must enter position that is greater than azimuth limit position!')
  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_set_el_position():
  logger.info('Set elevation position menu selected')
  curr_az, curr_el = get_encoder_positions_deg()
  while True:
    deg = raw_input('Enter desired elevation position in degrees or \'q\' to quit::')
    if deg == 'q' or deg == 'Q':
      break
    else:
      if float(deg) > 0.0:
        logger.info('Setting elevation position to: [{}] deg'.format(deg))
        move_x_deg = float(deg) - curr_el
        move_motors(deg_az=0.0, deg_el=float(move_x_deg),open_loop=True, skip_az=True)
        break
      else:
        logger.error('Must enter position that is greater than elevation limit position!')
  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_calibrate():
  logger.info('Calibration menu selected')
  calibrate_motors()
  
  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_set_loc():
  logger.info('Set Location menu selected')
  lat = raw_input('Enter Latitude:')
  lon = raw_input('Enter Latitude:')

  thismodule.latitude = float(lat); thismodule.longitude = float(lon)
  
  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_set_sys_time():
  logger.info('Set system time menu selected')
  time = raw_input('Enter system time in \'Nov 9 21:31:26\' format:')

  os.system('sudo date -s \"' + time + '\"')

  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


# TODO:
# def set_log_levels():


def menu_get_panel_pwr():
  logger.info('Get panel power menu selected')

  A, V, W = panel_power.get_all_measurements()
  logger.info('Current: [{}] A'.format(A))
  logger.info('Voltage: [{}] V'.format(V))
  logger.info('Power: [{}] W'.format(W))

  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_get_battery_pwr():
  logger.info('Get battery power menu selected')

  A, V, W = battery_power.get_all_measurements()
  logger.info('Current: [{}] A'.format(A))
  logger.info('Voltage: [{}] V'.format(V))
  logger.info('Power: [{}] W'.format(W))

  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def menu_get_all_pwr():
  logger.info('Get battery and panel power menu selected')

  samples = raw_input('Enter number of power measurements:')

  string = []
  string.append('Panel Current [A]')
  string.append('Panel Voltage [V]')
  string.append('Panel Power [W]')
  string.append('battery Current [A]')
  string.append('battery Voltage [V]')
  string.append('battery Power [W]')

  max_str_len = len( str(max(string, key=len)) )
  num_cols    = len(string)

  util_handle.write_table(string=string, max_str_len=max_str_len, header=True)

  for sample in range(int(samples)):
    data = []
    pan_A, pan_V, pan_W = panel_power.get_all_measurements()
    bat_A, bat_V, bat_W = battery_power.get_all_measurements()

    data.append(pan_A)
    data.append(pan_V)
    data.append(pan_W)
    data.append(bat_A)
    data.append(bat_V)
    data.append(bat_W)
    util_handle.write_table(string=data, max_str_len=max_str_len, header=False)

    time.sleep(0.25)

  raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


##########################
# Main Loop
##########################
def main_menu():  
  # change menu formatting
  menu_frmt = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.DOUBLE_LINE_BORDER) \
    .set_title_align('center') \
    .set_subtitle_align('center') \
    .set_left_margin(4) \
    .set_right_margin(4) \
    .show_header_bottom_border(True) \
    .show_prologue_top_border(True) \
    .show_prologue_bottom_border(True)

  # create main menu
  menu_title = 'PV Array Solar Tracking Menu'
  menu_subtitle = 'Select the desired menu option below'
  menu = ConsoleMenu(menu_title, menu_subtitle, formatter=menu_frmt)

  # Automatic tracking submenu
  auto_title = 'Automatic Tracking'
  auto_subtitle = 'Select from the desired modes below'
  auto_track_submenu = ConsoleMenu(auto_title, auto_subtitle, formatter=menu_frmt)

  ol_track_item = FunctionItem('Start Open Loop Tracking Mode', menu_open_loop)
  cl_track_item = FunctionItem('Start Closed Loop Tracking Mode', menu_closed_loop)

  auto_track_submenu.append_item(ol_track_item)
  auto_track_submenu.append_item(cl_track_item)

  auto_track_submenu_item = SubmenuItem(auto_title, submenu=auto_track_submenu)
  auto_track_submenu_item.set_menu(menu)

  # manual tracking submenu
  man_title = 'Manual Tracking'
  man_subtitle = 'Select from the desired modes below'
  man_track_submenu = ConsoleMenu(man_title, man_subtitle, formatter=menu_frmt)

  set_az_item  = FunctionItem('Set Azimuth Position', menu_set_az_position)
  set_el_item  = FunctionItem('Set Elevation Position', menu_set_el_position)
  sun_sim_item = FunctionItem('Open Loop User Defined Sun Simulation', menu_sun_simulation)

  man_track_submenu.append_item(set_az_item)
  man_track_submenu.append_item(set_el_item)
  man_track_submenu.append_item(sun_sim_item)

  man_track_submenu_item = SubmenuItem(man_title, submenu=man_track_submenu)
  man_track_submenu_item.set_menu(menu)

  # power measurement submenu
  pwr_title = 'Power Measurements'
  pwr_subtitle = 'Select from the desired modes below'
  pwr_track_submenu = ConsoleMenu(pwr_title, pwr_subtitle, formatter=menu_frmt)

  get_panel_pwr_item  = FunctionItem('Get Panel Power Measurements', menu_get_panel_pwr)
  get_batt_pwr_item   = FunctionItem('Get Battery Power Measurements', menu_get_battery_pwr)
  get_all_pwr_item    = FunctionItem('Get All System Power Measurements', menu_get_battery_pwr)

  pwr_track_submenu.append_item(get_panel_pwr_item)
  pwr_track_submenu.append_item(get_batt_pwr_item)
  pwr_track_submenu.append_item(get_all_pwr_item)

  pwr_track_submenu_item = SubmenuItem(pwr_title, submenu=pwr_track_submenu)
  pwr_track_submenu_item.set_menu(menu)

  # system configuration submenu
  conf_title = 'System Configuration'
  conf_subtitle = 'Select the desired menu option below'
  conf_track_submenu = ConsoleMenu(conf_title, conf_subtitle, formatter=menu_frmt)

  cal_sys_item = FunctionItem('Calibrate Shaft Encoders', menu_calibrate)
  set_loc_item = FunctionItem('Set System Latitude and Longitude', menu_set_loc)
  set_tim_item = FunctionItem('Set System Time Manually', menu_set_sys_time)

  conf_track_submenu.append_item(cal_sys_item)
  conf_track_submenu.append_item(set_loc_item)
  conf_track_submenu.append_item(set_tim_item)

  conf_submenu_item = SubmenuItem(conf_title, submenu=conf_track_submenu)
  conf_submenu_item.set_menu(menu)

  # TODO: create reset menu
  # TODO: add log level menu with options to change log level of each package
  #       make sure to also have the function start logging to file since it will
  #       be impossible to find info in console

  # Add all items to main menu
  menu.append_item(auto_track_submenu_item)
  menu.append_item(man_track_submenu_item)
  menu.append_item(pwr_track_submenu_item)
  menu.append_item(conf_submenu_item)

  # Show the menu
  menu.start()
  menu.join()
  
  
  
if __name__ == '__main__':
  # grab user flags
  parser = argparse.ArgumentParser(description='PV Array Solar Tracking Application')
  parser.add_argument('-m', '--menu', help='Start the development console menu', action='store_true')
  parser.add_argument('-s', '--sim', help='Start the sun simulation menu', action='store_true')
  parser.add_argument('-t', '--test', help='Start the position update menus', action='store_true')
  parser.add_argument('-v', '--verbose', help='Add verbose output', action='store_true')
  args = parser.parse_args()

  # TODO:
  if args.verbose:
    print('Verbosity NOT DEFINED')
    pass

  # TODO: how do we want to pull info from state file?
  # Run setup if needed
  print('\n' + '-'*50 + 'Running application setup' + '-'*50)
  init_pins()
  init_pi_hat()  
  init_interrupts()  
  # init_rtc()
  # NOTE: Mikes alg says to zero count, but we don't do that because the degree pos
  #       is calculated based on count.
  calibrate_motors()
  logger.info('Application setup complete')
  print('-'*125 + '\n')
  
  if args.menu:
    usr_ready = raw_input('Are you ready to open the menu interface? Press [ENTER] to continue')
    main_menu()
  elif args.sim:
    menu_sun_simulation()
  elif args.test:
    menu_move_az_x_deg()
    menu_move_el_x_deg()
  else:
    menu_normal_op()
  
  logger.info('Cleaning up all GPIO')
  GPIO.cleanup()

  # shutdown
  shutdown()
