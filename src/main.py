from datetime import datetime
import time
import logging
from astral import Astral
import geocoder

#NOTE: indentation is 2 spaces
  
# TODO: Need to set up pi to add this routine to startup -GN
# TODO: Need to find way to save state for periodically shutting down -GN
# TODO: Pass logger class or however you do it to sub-packages

#Global area
#wait time for easy readout of algorithm, will remove once everythin is implemented
t = 2

main_logger = logging.getLogger('main_logger')
main_logger.setLevel(logging.DEBUG)
# create console handler to log to the terminal
ch = logging.StreamHandler()
# set logging level to debug, will switch to info for final version
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to logger
main_logger.addHandler(ch)

lat = ""
long = ""
elev = ""
#End Global area

# todo: do not put all verbose config in single function
#       split out into setupPackageName(params) and define params
#       and call function here - GN
def setup():
  
  #Laod stored parameters
  main_logger.info('Loading stored prarmeters')
  #need to load from parameter file or similar, hard coded for now
  lat = 37.8
  long = -97.8
  elev = 6000
  time.sleep(t)
  
  #Load user specifice parameters
  main_logger.warn('Loading user specified parameters NOT DEFINED')
  time.sleep(t)
  
  #Get Location
  getLocation()
  
  #Calibrate system
  main_logger.info('Calibrating System NOT DEFINED')
  time.sleep(t)
  
#End setup()

# todo: possibly abstract some astral wrappers elsewhere -GN
def getLocation():
  global lat, long, elev
  try:
    main_logger.info('Getting location from IP')
    g = geocoder.ip('me')
    lat = g.latlng[0]
    long = g.latlng[1]
    main_logger.info('Get location from IP Successfull! =)')
  except:
    main_logger.warn('Get location from IP Failed, using defaults. =(')

  main_logger.info("Lattitude: [" + str(lat) + "], Longitude: [" + str(long) + "]")
  main_logger.info("Elevation: " + str(elev))
  
#End getLocation()

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
def main():
  # todo: very first step should be using the check_and_clear_alarms() from DS3231
  #       and verifying again that the alarms were cleared. If not, user needs to 
  #       be notified and some checks about if we can talk to the device should be done.
  #       if this happens, system cannot shutdown
  
  utc_now = datetime.utcnow()
  mm = str(utc_now.month)
  dd = str(utc_now.day)
  yyyy = str(utc_now.year)
  hour = str(utc_now.hour)
  mi = str(utc_now.minute)
  ss = str(utc_now.second)
  
  #US/Mountain  = timezone
  # todo: not sure we want to use utc time per mike's suggestions a couple weeks back
  #       ds3231 package converts to local, so logging time might be confusing and miss-aligned -GN
  # todo: For this, since you have datetime object, can use .strptime() or whatever the other one
  #       is to return utc time as specified parsed-order string -GN
  main_logger.info("Current UTC time: [" + mm + "/" + dd + "/" + yyyy + " " + hour + ":" + mi + ":" + ss + "]")

  #Run setup
  main_logger.info('Running setup')
  setup()
  time.sleep(t)
  
  #Get current position from shart encoders
  main_logger.warn('Get current position from shaft encoders NOT DEFINED')
  time.sleep(t)
  
  #Get current position from motors
  main_logger.warn('Get current position from motors NOT DEFINED')
  time.sleep(t)
  
  #Calculate sun position
  main_logger.debug('Calculate sun position')
  a = Astral()
  solarAz = a.solar_azimuth(datetime.utcnow(), lat, long)
  solarEl = a.solar_elevation(datetime.utcnow(), lat, long)
  main_logger.info("Current Solar Azimuth: [" + str(solarAz) + "], Current Solar Elevation: [" + str(solarEl) + "]")
  time.sleep(t) # todo: instead of sleeping, should be powering down

  # todo: call something here like initiateShutdownRoutine()
  #       I can take care of writing this when I get a chance as
  #       we have uC processes to take care of via GPIO -GN
  
#End main()

  
if __name__ == '__main__':
    main()
