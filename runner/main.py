#!/usr/bin/env python

from datetime import datetime, timedelta
import time
import logging
from astral import Astral, Location
import geocoder
import pytz
import os

import Adafruit_MCP3008 as ADC
import RPi.GPIO         as GPIO  

import sun_sensor
from utils             import utils, hardware
from DS3231            import DS3231
from motor_control     import stepper_motor
from shaft_encoder     import encoder
from system_monitor    import system_monitor
from power_measurement import power_measurement
from stepper_motor     import stepper_motor

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
# TODO: Mike
PIN_MOT_ELEVATION = None
PIN_MOT_AZIMUTH   = None
PIN_MOT_DIRECTION = None
PIN_MOT_CLOCK     = None
PIN_MOT_RESET     = None


##########################
# instantiate sub-modules
##########################
# User location
latitude  = 39.7392
longitude = 104.9903

# Logger
logger_name = 'main_app'
logger_rtc_name         = 'rtc'
logger_sys_mon_name     = 'sys_mon'
logger_panel_pwr_name   = 'panel_power'
logger_encoder_name     = 'shaft_encoder'
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
sys_mon = system_monitor( logger_name        = logger_name
                          logger_module_name = logger_sys_mon_name
                         )

# ADC
adc_vref     = 3.3
adc_num_bits = 10

adc_ch_panel_current     = 0
adc_ch_panel_voltage     = 3
adc_ch_battery_current   = 1
adc_ch_battery_voltage   = 2
adc_ch_up_right_sun_sens = 4 # can change since connections come in on header
adc_ch_up_left_sun_sens  = 5 # can change since connections come in on header
adc_ch_lo_right_sun_sens = 6 # can change since connections come in on header
adc_ch_lo_left_sun_sens  = 7 # can change since connections come in on header

adc = ADC.MCP3008( clk  = PIN_ADC_CLK,
                   cs   = PIN_ADC_CS,
                   miso = PIN_ADC_MISO,
                   mosi = PIN_ADC_MOSI
                  )

# Power Measurements
curr_sens_gain = 75

curr_sens_panel_Rshunt = 0.3
vdiv_panel_R1          = 1000
vdiv_panel_R2          = 160

curr_sens_battery_Rshunt = 0.001
vdiv_battery_R1          = 1000
vdiv_battery_R2          = 360

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
move_thresh_perc = 0.1

sun_sensor = sun_sensor( logger_name            = logger_name,
                         logger_module_name     = logger_sun_sensor_name,
                         move_motor_thresh_perc = move_thresh_perc,
                         adc_volt_ref           = adc_vref,
                         adc_ur_sens_ch         = adc_ch_up_right_sun_sens, 
                         adc_ul_sens_ch         = adc_ch_up_left_sun_sens,  
                         adc_lr_sens_ch         = adc_ch_lo_right_sun_sens, 
                         adc_ll_sens_ch         = adc_ch_lo_left_sun_sens,  
                         adc_object             = adc
                        )

# TODO: Shaft encoders here
# also note need to pull in stored parameters before hand to set counter in class each time system starts
shaft_encoder = encoder( logger_name        = logger_name,
                         logger_module_name = logger_encoder_name,
                        )

# TODO: motor control
az_steps_per_deg = 50
el_steps_per_deg = 62
motor = stepper_motor( logger_name        = logger_name,
                       logger_module_name = logger_motor_name,
                       pin_elevation      = PIN_MOT_ELEVATION,
                       pin_azimuth        = PIN_MOT_AZIMUTH,
                       pin_direction      = PIN_MOT_DIRECTION,
                       pin_clock          = PIN_MOT_CLOCK,
                       pin_reset          = PIN_MOT_RESET,
                       az_steps_per_deg   = az_steps_per_deg,
                       el_steps_per_deg   = el_steps_per_deg 
                      )

# Hardware abstraction
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

  # direction
  logger.info('Setting GPIO pin directions')
  # SE
  GPIO.setup(PIN_SE_AZIMUTH_A,   GPIO.IN)
  GPIO.setup(PIN_SE_AZIMUTH_B,   GPIO.IN)
  GPIO.setup(PIN_SE_ELEVATION_A, GPIO.IN)
  GPIO.setup(PIN_SE_ELEVATION_B, GPIO.IN)

  # ADC taken care of by package

  # ATTiny
  GPIO.setup(PIN_UC_PWR_ACK_TX,  GPIO.OUT)
  GPIO.setup(PIN_UC_FAULT_RX,    GPIO.IN)
  GPIO.setup(PIN_UC_DEV_MODE_RX, GPIO.IN)

  # Motors 
  # TODO: Mike


def init_pi_hat():
  logger.info('Setting Pi Hat ACK high')
  hw_handle.turn_pin_on(PIN_UC_PWR_ACK_TX)

  logger.info('Checking Pi Hat FAULT')
  if bit_is_set(PIN_UC_FAULT_RX):
    logger.error('Pi Hat power circuit FAULT! Check circuit and functionality before clearing condition!')
    # TODO: email user or something


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
def get_location(lat, lng):
  try:
    logger.info('Getting location from IP')
    g = geocoder.ip('me')
    lat = g.latlng[0]
    lng = g.latlng[1]
    logger.info('Get location from IP Successfull! =)')
  except:
    logger.warning('Get location from IP Failed, using defaults. =(')

  logger.info('Lattitude: [{}], Longitude: [{}]'.format(lat, lng))
  return lat, lng 
#End get_location


def get_location_astral(lat, lng, elev):
  loc = Location()
  loc.name = 'solar_tracker'
  loc.region = 'whereIam'
  loc.latitude = lat
  loc.longitude = lng
  loc.timezone = 'US/Mountain'
  loc.elevation = elev
  return loc
#End get_location_astral


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
  hw_handle.turn_pin_off(PIN_UC_PWR_ACK_TX) #uC will now wait ~45 seconds to pull power
  os.system('sudo shutdown now -h')
  '''
#End shutdown

def main():
  logger.info("Current UTC time: {}".format(datetime.utcnow())) # TODO: can remove once init_rtc() is uncommented
  
  #Run setup if needed
  logger.info('Running setup') # TODO: setup should happen outside of main
  
  #Load stored parameters
  logger.info('Loading stored prarmeters')
  #need to load from parameter file or similar, hard coded for now
  lat = 37.8
  long = -97.8
  elev = 6000
  
  prev_solar_az = 123.0
  prev_solar_el = 16.0
  
  #Load user specifice parameters
  logger.warn('Loading user specified parameters NOT DEFINED')
  
  #Get Location
  lat, lng = get_location(lat, long)
  
  #Get astral with current location
  loc_astral = get_location_astral(lat, lng, elev)
  
  #Calibrate system
  logger.info('Calibrating System NOT DEFINED')
  
  sun_dict = loc_astral.sun()
  now = pytz.timezone('US/Mountain').localize(datetime.now())
  
  #Get current position from shart encoders
  # TODO: lol ^^^
  logger.warning('Get current position from shaft encoders NOT DEFINED')
  encoder_az = encoder(5,11,2000) # TODO: Use format I have defined above
  #a is 29 on PI
  #b is 23 on PI
  init_encoder_az = encoder_az.get_degrees()
  logger.info('Shaft encoder initial: [{}]'.format(init_encoder_az))
  
  #Get current position from motors
  logger.warn('Get current position from motors NOT DEFINED')
  
  if now > sun_dict['sunrise'] and now < sun_dict['sunset']:
    daytime = True
    print("Daytime")
  else:
    daytime = False
    print("Nighttime")
    
  if daytime: #this will be the if check from above, implemented this way for development
    #Get solar position
    solar_az = loc_astral.solar_azimuth(datetime.now())
    solar_el = loc_astral.solar_elevation(datetime.now())
    logger.info('Next Solar Azimuth: [{}], Next Solar Elevation: [{}]'.format(solar_az, solar_el))
    
    #Move to calculated sun posistion
    motor = stepper_motor()
    deg_az = int(round(solar_az - prev_solar_az)) # TODO: why are we rounding?
    if deg_az < 0:
      #dir = stepper_motor.EAST
      dir = 0
    else:
      #dir = stepper_motor.WEST
      dir = 1
    #motor.move_motor(stepper_motor.AZ, dir, deg_az)
    motor.move_motor(19, dir, deg_az)
    
    deg_el = int(round(solar_el - prev_solar_el)) # TODO: reference note above about rounding
    if deg_el < 0:
      #dir = stepper_motor.SOUTH
      dir = 0
    else:
      #dir = stepper_motor.NORTH
      dir = 1
    #motor.move_motor(stepper_motor.EL, dir, deg_el)
    motor.move_motor(13, dir, deg_el)

    final_encoder_az = encoder_az.get_degrees()
    logger.info('Shaft encoder final: [{}]'.format(final_encoder_az))

    degrees_move_encoder = final_encoder_az - init_encoder_az
    logger.info('Shaft encoder degrees moved: [{}]'.format(degrees_move_encoder))
    
    #Read light sensor
    logger.info('Reading light sensor')
    
  else:
    #Get solar position for tomorrow morning
    tomorrow = datetime.today() + timedelta(days=1)
    sun_dict = loc_astral.sun(tomorrow.date())
    solar_az = loc_astral.solar_azimuth(sun_dict['sunrise'])
    solar_el = loc_astral.solar_elevation(sun_dict['sunrise'])
    logger.info('Tomorrow Solar Azimuth: [{}], Tomorrow Solar Elevation: [{}]'.format(solar_az, solar_el)) #.format() is literally the only useful thing I learned from Pete...
    
    #Move to sunrise position for tomorrow
    logger.info('Moving to sunrise position for tomorrow NOT DEFINED')
  #End if else

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
  # init_pins()
  # init_pi_hat()
  # init_rtc()
  main()
