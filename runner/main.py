#!/usr/bin/env python

from datetime import datetime, timedelta
import time
import logging
from astral import Astral, Location
import pytz
import os

import RPi.GPIO         as GPIO
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
  # TODO: add below
  # motor.configure_limit_switch_INT()


def init_rtc():
  # Checking RTC alarms
  rtc.check_and_clear_alarms()

  # Initial checks for time accuracy
  rtc_now, local_now, delta = rtc.get_datetime_delta(return_all=True)

  # config rtc
  if delta.days > 0:
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
# TODO: where should these go
def get_encoder_degrees_all():
  logger.info('Get current position from shaft encoders')
  az_deg = az_encoder.get_degrees()
  el_deg = el_encoder.get_degrees()
  logger.info('Shaft encoder azimuth: [{}] deg'.format(init_encoder_az))
  logger.info('Shaft encoder elevation: [{}] deg'.format(init_encoder_el))
  return az_deg, el_deg


def get_location_astral(lat, lng, elev):
  loc = Location()
  loc.name = 'solar_tracker'
  loc.region = 'whereIam'
  loc.latitude = lat
  loc.longitude = lng
  loc.timezone = 'US/Mountain'
  loc.elevation = elev # TODO: do we need this?
  logger.info('Astral location: {}'.format(loc))
  return loc


def get_solar_position_deg(loc_astral):
  az_deg = loc_astral.solar_azimuth(datetime.now())
  el_deg = loc_astral.solar_elevation(datetime.now())
  logger.info('Next Solar Azimuth: [{}] deg'.format(az_deg))
  logger.info('Next solar elevation: [{}] deg'.format(el_deg))
  return az_deg, el_deg


def is_daytime():
  now = datetime..now()
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


  
##########################
# Main Loop
##########################
def main():
  logger.info("Current UTC time: {}".format(datetime.utcnow())) # TODO: can remove once init_rtc() is uncommented
  
  #Run setup if needed
  logger.info('Running setup') # TODO: setup should happen outside of main
  
  #Load stored parameters
  logger.info('Loading stored prarmeters NOT DEFINED')
  
  prev_solar_az = 242.0
  prev_solar_el = 7.0
  
  #Load user specifice parameters
  logger.warn('Loading user specified parameters NOT DEFINED')
  
  #Get astral with current location
  loc_astral = get_location_astral(latitude, longitude, elevation)
  
  # Calibrate system
  logger.warn('Calibrating System NOT DEFINED')
  
  sun_dict = loc_astral.sun()
  now = datetime.now()
  #now = pytz.timezone('US/Mountain').localize(datetime.now())
  #logger.info('pytz datetime: {}, dt datetime: {}'.format(now, datetime.now())) # TODO: both basically same, I think we should remove pytz

  # Get current position from shart encoders
  # lol ^^^
  init_encoder_deg_az, init_encoder_deg_el = get_encoder_degrees_all()
  
  # Get current position from motors
  # TODO: We should be trusting encoders only, so I'm not sure if this is needed
  logger.warn('Get current position from motors NOT DEFINED')
  
  if is_daytime(): #this will be the if check from above, implemented this way for development
    #Get solar position
    solar_deg_az, solar_deg_el = get_solar_position_deg(loc_astral)
    
    #Move to calculated sun posistion
    deg_az = solar_deg_az - prev_solar_az
    if deg_az < 0:
      dir_az = MotorCtrl_t.EAST
    else:
      dir_az = MotorCtrl_t.WEST
    logger.info('Moving azimuth {} degrees {}'.format(deg_az, dir_az))
    #motor.move_motor(PIN_MOT_AZIMUTH, dir_az, deg_az)
    
    deg_el = solar_deg_el - prev_solar_el 
    if deg_el < 0:
      dir_el = MotorCtrl_t.SOUTH
    else:
      dir_el = MotorCtrl_t.NORTH
    logger.info('Moving elevation {} degrees {}'.format(deg_el, dir_el))
    #motor.move_motor(PIN_MOT_ELEVATION, dir_el, deg_el)

    final_encoder_az = az_encoder.get_degrees()
    logger.info('Azimuth shaft encoder final: [{}]'.format(final_encoder_az))
    
    final_encoder_el = el_encoder.get_degrees()
    logger.info('Elevation shaft encoder final: [{}]'.format(final_encoder_el))

    degrees_move_az = final_encoder_az - init_encoder_az
    logger.info('Azimuth shaft encoder degrees moved: [{}]'.format(degrees_move_az))
    
    degrees_move_el = final_encoder_el - init_encoder_el
    logger.info('Elevation shaft encoder degrees moved: [{}]'.format(degrees_move_el))
    
    #Read light sensor
    # TODO: is above referring to limit switch? If so, I am taking care of this in motor class
    logger.info('Reading light sensor')
    
  else:
    #Get solar position for tomorrow morning
    tomorrow = datetime.today() + timedelta(days=1)
    sun_dict = loc_astral.sun(tomorrow.date())
    solar_deg_az = loc_astral.solar_azimuth(sun_dict['sunrise'])
    solar_deg_el = loc_astral.solar_elevation(sun_dict['sunrise'])
    logger.info('Tomorrow Solar Azimuth: [{}], Tomorrow Solar Elevation: [{}]'.format(solar_deg_az, solar_deg_el))
    
    #Move to sunrise position for tomorrow
    logger.info('Moving to sunrise position for tomorrow NOT DEFINED')
  
  # test loop for tracking light
  while 1:
    az_dir, el_dir = sun_sensors.get_motor_direction_all()
    logger.info('Desired azimuth direction: {}'.format(az_dir))
    logger.info('Desired elevation direction: {}'.format(el_dir))
    motor.move_motor(PIN_MOT_ELEVATION, el_dir, 0.5)
    motor.move_motor(PIN_MOT_AZIMUTH, az_dir, 0.5)
    #time.sleep(0.01)

  # TODO: use GPIO.cleanup() or GPIO.cleanup([channels]) somewhere before shutdown.
  #       cleanup() may cause issues with AVRDude, so specifying used channels as [] or () is probably needed
  # TODO: check pin_is_set(PIN_UC_DEV_MODE_RX) to determine if we will use time.sleep() for the desired amount of time
  #       or if we can actually shutdown and set an alarm. If true, must operate inside a while True: loop and send email to user 
  #       if they forget to take the device out of dev mode after an hour or something.
  # TODO: measure power of shutdown/power up to see if it is worth it during day. If it is, make sure we aren't shutting down if next alarm will be
  #       before amount of time it takes to shutdown
  shutdown()
  
#End main()

  
if __name__ == '__main__':
  # TODO: need to add check at beginning for log levels
  # TODO: how do we want to pull info from state file?
  init_pins()
  init_pi_hat()
  init_interrupts()
  # init_rtc()
  main()
