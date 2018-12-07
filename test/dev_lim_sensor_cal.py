import RPi.GPIO as MOT
import time
MOT.setwarnings(False)
MOT.setmode(MOT.BCM)
EL = 18
AZ = 17
MOT.setup(18,MOT.IN)
MOT.setup(17,MOT.IN)
while(not MOT.input(EL)):
  print(MOT.input(EL))


