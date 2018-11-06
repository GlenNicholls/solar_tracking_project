import RPi.GPIO as MOT
import time

#TODO: Define a constants file???
#Constants
WEST = 0
NORTH = 0
EAST = 1
SOUTH = 1
ENABLE = 1
DISABLE = 0
DIR = 12 #12-direction (17
EL = 13 #13-EL controller enable (10)
CLK = 16 #16-clock (18)
AZ = 19 #19-AZ controller enable (10)
RST = 26 #26-reset (20
DEGAZ = 50 #Number of steps for 1 degree of movement in azimuth
DEGEL = 62 #Number of steps for 1 degree of movement in elevation
SPEED = 0.001 #Time delay to control the speed

class stepper_motor:

  def __init__(self): 
    MOT.setwarnings(False)
    MOT.setmode(MOT.BCM)
    lines = [DIR, EL, CLK, AZ, RST] # TODO: Make this part of class init
    for pin in lines:  #sets pins 12,13,16,19,26 as outputs
        MOT.setup(pin,MOT.OUT)
  #End __init__
  
  #TODO: Pass parameters using enum
  def move_motor(self, axis, dir, deg):
    if axis == AZ:
      steps = deg*DEGAZ
    elif axis == EL:
      steps = deg*DEGEL
    else:
      return
      
    MOT.output(CLK,ENABLE)  #sets clock pin high, falling edge
    MOT.output(DIR,dir)  #sets motor direction 1 = W/N, 0 = E/S
    MOT.output(axis,DISABLE)
    MOT.output(RST,1)  #resets to starting configuration 1010
    MOT.output(RST,0)  #starts reset
    MOT.output(RST,1)  #ends reset
    MOT.output(axis,ENABLE)
      
    for step in range(0, steps):
      MOT.output(CLK, DISABLE)  #pulse the clock pin
      time.sleep(SPEED)
      MOT.output(CLK, ENABLE)
      time.sleep(SPEED)
    
    MOT.output(axis, DISABLE)
  #End move_motor
  
#End stepper_motor
