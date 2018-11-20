#!/usr/bin/env python

import sys
import time
import logging
from datetime import datetime, timedelta
from astral import Astral, Location
import pytz
import os

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
PIN_SE_AZIMUTH_A   = 5  
PIN_SE_AZIMUTH_B   = 11 
PIN_SE_ELEVATION_A = 26 
PIN_SE_ELEVATION_B = 13 

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
PIN_MOT_ELEVATION = 27
PIN_MOT_AZIMUTH   = 22
PIN_MOT_RESET     = 6
PIN_MOT_CLOCK     = 9
PIN_MOT_DIRECTION = 1

# Limit switches
PIN_LIM_SW_AZIMUTH   = 17
PIN_LIM_SW_ELEVATION = 18


##########################
# instantiate sub-modules
##########################
# User location
latitude  = 38.893950
longitude = -104.800898
elevation = 6000

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
              latitude           = latitude,
              longitude          = longitude
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
  GPIO.setup(PIN_MOT_ELEVATION, GPIO.OUT)
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
  motor.move_motor(PIN_MOT_AZIMUTH, direction, degrees)


def move_motor_el(direction, degrees):
  logger.info('Moving elevation [{}] degrees [{}]'.format(degrees, direction))
  motor.move_motor(PIN_MOT_ELEVATION, direction, degrees)


def move_motors_open_loop(deg_az, deg_el):
  locked = False
  locked_az = False
  locked_el = False
  enc_thresh = 0.25 # defining tight threshold for motors

  # create constant to generate error term later without multiplier
  desired_deg_az = deg_az
  desired_deg_el = deg_el

  # if encoders aren't reading correct position, loop
  while not locked: # and check_cnt < some_number:
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
    deg_az = new_deg_az - desired_deg_az
    deg_el = new_deg_el - desired_deg_el
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
      locked_az = True
    elif not locked_el:
      logger.warn('Desired Elevation: [{}] deg'.format(desired_deg_el))
      logger.warn('Current Elevation: [{}] deg'.format(new_deg_el))
      logger.warn('Elevation error: [{}] deg'.format(err_deg_el))

    if locked_az and locked_el:
      logger.info('Azimuth and elevation are locked!!!')
      locked = True

  logger.info('Azimuth shaft encoder final: [{}]'.format(new_deg_az))
  logger.info('Elevation shaft encoder final: [{}]'.format(new_deg_el))
  return locked
  

def move_motors_closed_loop():
  locked = False
  move_mot_deg = 0.5

  while not locked:
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
  return locked


def move_motors(deg_az=None, deg_el=None, open_loop=False, closed_loop=False):
  if open_loop and closed_loop:
    raise ValueError('Must select open loop OR closed loop, not both!')
  if open_loop and (deg_az == None or deg_az == None):
    raise ValueError('Must enter movement values for BOTH azimuth and elevation')
  if closed_loop and (deg_az != None or deg_el != None):
    self.logger.warn('Ignoring program calculated azimuth and elevation degree movements in closed loop mode!')

  if open_loop:
    logger.info('Open loop tracking initiated')
    move_motors_open_loop(deg_az, deg_el)
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
def normal_op_menu():
  #Load stored parameters
  logger.warn('Loading stored prarmeters NOT DEFINED')
  
  prev_solar_az = 242.0
  prev_solar_el = 7.0
  
  #Load user specifice parameters
  logger.warn('Loading user specified parameters NOT DEFINED')
  
  #Get astral with current location
  loc_astral = get_location_astral(latitude, longitude, elevation)
  
  # Calibrate system
  logger.warn('Calibrating System NOT DEFINED')
    
  # Get current position from motors
  # TODO: We should be trusting encoders only, so I'm not sure if this is needed
  logger.warn('Get current position from motors NOT DEFINED')
  
  if is_daytime(loc_astral): #this will be the if check from above, implemented this way for development
    # Get solar position
    solar_deg_az, solar_deg_el = get_solar_position_deg(loc_astral)
    
    # Move to calculated sun posistion
    deg_az = solar_deg_az - prev_solar_az
    deg_el = solar_deg_el - prev_solar_el 
    open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)
    
    # Perform fine adjustments
    closed_loop_locked = move_motors(closed_loop=True)
    # TODO: ensure we're locked still

    #Read light sensor
    # TODO: is this referring to limit switch? If so, I am taking care of this in motor class -GN
    logger.info('Reading light sensor')
    
  else:
    #Get solar position for tomorrow morning
    solar_deg_az, solar_deg_el = get_sunrise_position_deg(loc_astral)
    
    #Move to sunrise position for tomorrow
    logger.warn('Moving to sunrise position for tomorrow NOT DEFINED')

  # TODO: use GPIO.cleanup() or GPIO.cleanup([channels]) somewhere before shutdown.
  #       cleanup() may cause issues with AVRDude, so specifying used channels as [] or () is probably needed
  # TODO: check pin_is_set(PIN_UC_DEV_MODE_RX) to determine if we will use time.sleep() for the desired amount of time
  #       or if we can actually shutdown and set an alarm. If true, must operate inside a while True: loop and send email to user 
  #       if they forget to take the device out of dev mode after an hour or something.
  # TODO: measure power of shutdown/power up to see if it is worth it during day. If it is, make sure we aren't shutting down if next alarm will be
  #       before amount of time it takes to shutdown

  usr_ready = raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


# TODO:
def open_loop_menu():
  logger.info('Open loop tracking menu selected')

  prev_solar_az = 242.0
  prev_solar_el = 7.0
  
  #Get astral with current location
  loc_astral = get_location_astral(latitude, longitude, elevation)
  
  if is_daytime(loc_astral): #this will be the if check from above, implemented this way for development
    # Get solar position
    solar_deg_az, solar_deg_el = get_solar_position_deg(loc_astral)
    
    # Move to calculated sun posistion
    deg_az = solar_deg_az - prev_solar_az
    deg_el = solar_deg_el - prev_solar_el 
    open_loop_locked = move_motors(deg_az, deg_el, open_loop=True)
  else:
    #Get solar position for tomorrow morning
    solar_deg_az, solar_deg_el = get_sunrise_position_deg(loc_astral)
    
    #Move to sunrise position for tomorrow
    logger.warn('Moving to sunrise position for tomorrow NOT DEFINED')

  usr_ready = raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')

def closed_loop_menu():
  logger.info('Closed loop tracking menu selected')
  closed_loop_locked = move_motors(closed_loop=True)
  usr_ready = raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')
    


def set_azimuth_menu():
  deg = raw_input('Enter an value in degrees:')
  logger.info('Setting azimuth position to: [{}] deg'.format(deg))
  move_motors(deg_az=float(deg), deg_el=0.0,open_loop=True)
  usr_ready = raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')


def set_elevation_menu():
  deg = raw_input('Enter an value in degrees:')
  logger.info('Setting elevation position to: [{}] deg'.format(deg))
  move_motors(deg_az=0.0, deg_el=float(deg),open_loop=True)
  usr_ready = raw_input('Are you ready to go back to the menu? Press [ENTER] to continue')

# TODO:
# def set_lat_long()
# def reset_azimuth():
# def reset_elevation():


##########################
# Main Loop
##########################
def main():  
  # change menu formatting
  menu_frmt = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
    .set_title_align('center') \
    .set_subtitle_align('center') \
    .set_left_margin(4) \
    .set_right_margin(4) \
    .show_header_bottom_border(True)

  # create main menu
  menu_title = 'PV Array Solar Tracking Menu'
  menu_subtitle = 'Select the desired mode of operation from the list below'
  menu = ConsoleMenu(menu_title, menu_subtitle, formatter=menu_frmt)

  # create normal tracking menu
  normal_track_item = FunctionItem('Start Normal Tracking Mode', normal_op_menu)

  # create open loop tracking menu
  ol_track_item = FunctionItem('Start Open Loop Tracking Mode', open_loop_menu)

  # create closed loop tracking menu
  cl_track_item = FunctionItem('Start Closed Loop Tracking Mode', closed_loop_menu)

  # manual tracking submenu
  man_title = 'Manual Tracking'
  man_subtitle = 'Select an update for azimuth or elevation'
  man_track_submenu = ConsoleMenu(man_title, man_subtitle, formatter=menu_frmt)

  man_track_az = FunctionItem('Set Azimuth Position', set_azimuth_menu)
  man_track_el = FunctionItem('Set Elevation Position', set_elevation_menu)

  man_track_submenu.append_item(man_track_az)
  man_track_submenu.append_item(man_track_el)

  man_track_submenu_item = SubmenuItem(man_title, submenu=man_track_submenu)
  man_track_submenu_item.set_menu(menu)

  # TODO: create calibration menu
  # TODO: create reset menu
  # TODO: create lat/long menu

  # Add all items to main menu
  menu.append_item(normal_track_item)
  menu.append_item(ol_track_item)
  menu.append_item(cl_track_item)
  menu.append_item(man_track_submenu_item)

  # Show the menu
  menu.start()
  menu.join()
  
  
  
if __name__ == '__main__':
  # TODO: need to add check at beginning for log levels
  # TODO: how do we want to pull info from state file?
  # Run setup if needed
  print('\n' + '-'*50 + 'Running application setup' + '-'*50)
  init_pins()
  init_pi_hat()
  init_interrupts()
  # init_rtc()
  logger.info('Application setup complete')
  print('-'*125 + '\n')

  usr_ready = raw_input('Are you ready to open the menu interface? Press [ENTER] to continue')

  main()

  logger.info('Cleaning up all GPIO')
  GPIO.cleanup()

  # shutdown
  shutdown()
