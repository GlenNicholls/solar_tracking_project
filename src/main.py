#!/usr/bin/env python
from datetime import datetime
from datetime import timedelta
import time
import logging
from astral import Astral
from astral import Location
import geocoder
import pytz
import os

#NOTE: indentation is 2 spaces
  
# TODO: Need to set up pi to add this routine to startup -GN
# TODO: Need to find way to save state for periodically shutting down -GN
# TODO: Pass logger class or however you do it to sub-packages

#Global area
main_logger = logging.getLogger('main_logger')
main_logger.setLevel(logging.DEBUG)
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
main_logger.addHandler(ch)
#End Global area

def get_location(lat, lng):
  try:
    main_logger.info('Getting location from IP')
    g = geocoder.ip('me')
    lat = g.latlng[0]
    lng = g.latlng[1]
    main_logger.info('Get location from IP Successfull! =)')
  except:
    main_logger.warn('Get location from IP Failed, using defaults. =(')

  main_logger.info("Lattitude: [" + str(lat) + "], Longitude: [" + str(lng) + "]")
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
3) before shutdown, need to check dev mode pin from uC. If high, needs to 
   periodically check for this. If doesn't go low for long time, notify user
4) once dev mode pin from uC is low, then drive ack pin to uC low and commence
   >>> shutdown -h now immediately
5) will think about other cases that need to be accounted for in here
'''

def shutdown():
  main_logger.info('Initiating Shutdown')
  #os.system('shutdown now -h')
#End shutdown

def main():
  # todo: very first step should be using the check_and_clear_alarms() from DS3231
  #       and verifying again that the alarms were cleared. If not, user needs to 
  #       be notified and some checks about if we can talk to the device should be done.
  #       if this happens, system cannot shutdown
 
  main_logger.info("Current UTC time: " + str(datetime.utcnow()))
  
  #Run setup if needed
  main_logger.info('Running setup')
  
  #Load stored parameters
  main_logger.info('Loading stored prarmeters')
  #need to load from parameter file or similar, hard coded for now
  lat = 37.8
  long = -97.8
  elev = 6000
  
  #Load user specifice parameters
  main_logger.warn('Loading user specified parameters NOT DEFINED')
  
  #Get Location
  lat, lng = get_location(lat, long)
  
  #Get astral with current location
  loc_astral = get_location_astral(lat, lng, elev)
  
  #Calibrate system
  main_logger.info('Calibrating System NOT DEFINED')
  
  sun_dict = loc_astral.sun()
  now = pytz.timezone('US/Mountain').localize(datetime.now())
  
  #Get current position from shart encoders
  main_logger.warn('Get current position from shaft encoders NOT DEFINED')
  
  #Get current position from motors
  main_logger.warn('Get current position from motors NOT DEFINED')
  
  if now > sun_dict['sunrise'] and now < sun_dict['sunset']:
    daytime = True
    print("Daytime")
  else:
    daytime = False
    print("Nighttime")
    
  if not daytime: #this will be the if check from above, implemented this way for development
    #Get solar position
    solar_az = loc_astral.solar_azimuth(datetime.now())
    solar_el = loc_astral.solar_elevation(datetime.now())
    main_logger.info("Next Solar Azimuth: [" + str(solar_az) + "], Next Solar Elevation: [" + str(solar_el) + "]")
    
    #Move to calculated sun posistion
    main_logger.info('Moving to next position NOT DEFINED')
    
    #Read light sensor
    main_logger.info('Reading light sensor')
    
  else:
    #Get solar position for tomorrow morning
    tomorrow = datetime.today() + timedelta(days=1)
    sun_dict = loc_astral.sun(tomorrow.date())
    solar_az = loc_astral.solar_azimuth(sun_dict['sunrise'])
    solar_el = loc_astral.solar_elevation(sun_dict['sunrise'])
    main_logger.info("Tomorrow Solar Azimuth: [" + str(solar_az) + "], Tomorrow Solar Elevation: [" + str(solar_el) + "]")
    
    #Move to sunrise position for tomorrow
    main_logger.info('Moving to sunrise position for tomorrow NOT DEFINED')
  #End if else

  shutdown()
  
#End main()

  
if __name__ == '__main__':
    main()
