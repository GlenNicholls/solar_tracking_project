from datetime import datetime
import time
import logging
from astral import Astral
import geocoder

#NOTE: indentation is 2 spaces
  
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


def main():
  
  utc_now = datetime.utcnow()
  mm = str(utc_now.month)
  dd = str(utc_now.day)
  yyyy = str(utc_now.year)
  hour = str(utc_now.hour)
  mi = str(utc_now.minute)
  ss = str(utc_now.second)
  
  #US/Mountain  = timezone

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
  time.sleep(t)
  
#End main()

  
if __name__ == '__main__':
    main()
