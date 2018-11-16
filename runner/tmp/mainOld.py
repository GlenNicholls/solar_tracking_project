#!/usr/bin/env python

from datetime import datetime, timedelta
import time
import logging
from astral import Astral, Location
import geocoder
import pytz
import os
from DS3231         import DS3231
from motor_control  import stepper_motor
from shaft_encoder  import encoder
from system_monitor import system_monitor
import Adafruit_MCP3008 as ADC

#NOTE: indentation is 2 spaces
  
# TODO: Need to set up pi to add this main.py routine to startup -GN
# TODO: Need to find way to save state for periodically shutting down -GN

# pin definitions here
#
#
#
i2c_port  = 1 # set to 0 if using gen 1 pi
i2c_addr  = 0x68
latitude  = 39.7392
longitude = 104.9903


#Global area
# TODO: possibly add init_logger()
logger_name = 'main_app'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
# create console handler to log to the terminal
ch = logging.StreamHandler()
# create file handler to log the state for next reboot
#fh = logging.FileHandler('state.log')
# set logging level to debug, will switch to info for final version
ch.setLevel(logging.DEBUG)
#fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
#End Global area


##########################
# instantiate sub-modules
##########################
rtc = DS3231(logger    = logger_name,
             i2c_port  = i2c_port,
             i2c_addr  = i2c_addr,
             latitude  = latitude,
             longitude = longitude)

sys_mon = system_monitor(logger = logger_name)


##########################
# init packages
##########################
def init_rtc():
  rtc.configure_rtc()

  # Initial checks for time accuracy
  logger.info('Checking time')
  logger.info('RTCs current time: {}'.format(rtc.get_datetime_str()))
  logger.info('Current NTP time: {}'.format(datetime.datetime.now()))

  # update RTC if power was lost or if we have internet connection
  logger.info('Checking to see if power was lost or if there is an internet connection')
  if rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.set_datetime_now()
    logger.info('Power was lost, time updated to: {}'.format(rtc.get_datetime_str()))
  elif rtc.get_power_lost() and not sys_mon.is_wlan_connected():
    logger.error('Power was lost and no internet connection, cannot update time!')
  elif not rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.set_datetime_now()
    logger.info('There is an internet connection and power was not lost')
    logger.info('Time updated to: {}'.format(rtc.get_datetime_str()))
  else:
    logger.info('Power was not lost and no connection to update time')

# TODO: add get_all_params() and print these
# def init_sys_mon():


##########################
# Helpers
##########################
def get_location(lat, lng):
  try:
    logger.info('Getting location from IP')
    g = geocoder.ip('me')
    lat = g.latlng[0]
    lng = g.latlng[1]
    logger.info('Get location from IP Successfull! =)')
  except:
    logger.warn('Get location from IP Failed, using defaults. =(')

  logger.info("Lattitude: [" + str(lat) + "], Longitude: [" + str(lng) + "]")
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
1) startup should drive uC ack pin high
2) FAULT pin should be an interrupt. If this ever goes high, need to somehow
   issue text/email/tweet notifying user that uC has experienced an issue
4) once dev mode pin from uC is low, then drive ack pin to uC low and commence
   >>> shutdown -h now immediately
5) will think about other cases that need to be accounted for in here
'''

def shutdown():
  logger.info('Initiating Shutdown')

  # TODO: logic below
  '''
  while DEV_MODE_PIN_IS_ON:
    sleep(some time) # set timer and after really long time issue error

  # if we want to power down between update periods do this, else set alarm for sunrise
  if (periodic sleep during tracking is desired):
    # TODO: change name to set_alarm_delta() as this name seems dumb now that I read it again
    rtc.set_alarm_now_delta(minutes=?, seconds=?) # values propagated down and calculation done based on user update deg frequency
  else:
    rtc.set_alarm_sunrise()
  ack_pin = 0
  os.system('shutdown now -h')
  '''
#End shutdown

def main():
  # todo: very first step should be using the check_and_clear_alarms() from DS3231
  #       and verifying again that the alarms were cleared. If not, user needs to 
  #       be notified and some checks about if we can talk to the device should be done.
  #       if this happens, system cannot shutdown
 
  logger.info("Current UTC time: {}".format(datetime.utcnow()))
  
  #Run setup if needed
  logger.info('Running setup')
  #Move these to a constants file???
  CLK  = 18
  MISO = 23
  MOSI = 24
  CS   = 25
  adc = ADC.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
  
  #Load stored parameters
  logger.info('Loading stored prarmeters')
  #need to load from parameter file or similar, hard coded for now
  lat = 37.8
  long = -97.8
  elev = 6000
  
  prev_solar_az = 190.0
  prev_solar_el = 28.0
  
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
  logger.warn('Get current position from shaft encoders NOT DEFINED')
  encoder_az = encoder(5,11,2000)
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
    deg_az = int(round(solar_az - prev_solar_az))
    if deg_az < 0:
      #dir = stepper_motor.EAST
      dir = 1
    else:
      #dir = stepper_motor.WEST
      dir = 0
    #motor.move_motor(stepper_motor.AZ, dir, deg_az)
    motor.move_motor(19, dir, deg_az)
    
    deg_el = int(round(solar_el - prev_solar_el))
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

  shutdown()
  
#End main()

  
if __name__ == '__main__':
    main()
