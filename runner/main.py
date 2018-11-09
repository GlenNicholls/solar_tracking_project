#!/usr/bin/env python

from datetime import datetime, timedelta
import time
import logging
from astral import Astral, Location
import geocoder
import pytz
import os

import sun_sensor
import Adafruit_MCP3008 as ADC
from utils             import utils
from DS3231            import DS3231
from motor_control     import stepper_motor
from shaft_encoder     import encoder
from system_monitor    import system_monitor
from power_measurement import power_measurement

#NOTE: indentation is 2 spaces
  
# TODO: Need to set up pi to add this main.py routine to startup -GN
# TODO: Need to find way to save state for periodically shutting down -GN

##########################
# GPIO Pin Definitions
##########################
# Shaft Encoders
GPIO_SE_AZIMUTH_A   = 5  # TODO: BCM??
GPIO_SE_AZIMUTH_B   = 11 # TODO: BCM??
GPIO_SE_ELEVATION_A = 26 # TODO: BCM??
GPIO_SE_ELEVATION_B = 13 # TODO: BCM??

# ADC
GPIO_ADC_CLK  = 21 # BCM pin numbering
GPIO_ADC_MISO = 19 # BCM pin numbering
GPIO_ADC_MOSI = 20 # BCM pin numbering
GPIO_ADC_CS   = 10 # BCM pin numbering

# RTC is accounted for based on I2C channel

# ATTiny
# Program pins accounted for in Makefile
GPIO_UC_PWR_ACK_TX  = 25 # TODO: BCM??
GPIO_UC_FAULT_RX    = 7  # TODO: BCM??
GPIO_UC_DEV_MODE_RX = 8  # TODO: BCM??

# Motor Control
# TODO: Mike

# TODO: add init_pins() to init directions and such

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
logger_panel_pwr_name   = 'battery_power'
logger_sun_sensor_name  = 'sun_sensor'

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

adc = ADC.MCP3008( clk  = GPIO_ADC_CLK,
                   cs   = GPIO_ADC_CS,
                   miso = GPIO_ADC_MISO,
                   mosi = GPIO_ADC_MOSI
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
                                   logger_module_name   = logger_panel_pwr_name,
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
    logger.warning('Power was lost and no internet connection, cannot update time!')
  elif not rtc.get_power_lost() and sys_mon.is_wlan_connected():
    rtc.set_datetime_now()
    logger.info('There is an internet connection and power was not lost')
    logger.info('Time updated to: {}'.format(rtc.get_datetime_str()))
  else:
    logger.warning('Power was not lost and no connection to update time')

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
1) startup should drive uC ack pin high
2) FAULT pin should be an interrupt. If this ever goes high, need to somehow
   issue text/email/tweet notifying user that uC has experienced an issue
4) once dev mode pin from uC is low, then drive ack pin to uC low and commence
   >>> shutdown -h now immediately
5) will think about other cases that need to be accounted for in here
'''

def shutdown():
  # TODO: add flag for nighttime and add this to rtc.set_alarm_sunrise() check
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
  logger.warn('Get current position from shaft encoders NOT DEFINED')
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
    deg_az = int(round(solar_az - prev_solar_az))
    if deg_az < 0:
      #dir = stepper_motor.EAST
      dir = 0
    else:
      #dir = stepper_motor.WEST
      dir = 1
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
