import RPi.GPIO as MOT
import time
MOT.setwarnings(False)
MOT.setmode(MOT.BCM)
lines = [12,16,21,26]
for pin in lines:  #initialize pins 12,16,21 and 26 as outputs
    MOT.setup(pin,MOT.OUT)
#MOT.setup(16,MOT.OUT)
#MOT.setup(21,MOT.OUT)
#MOT.setup(26,MOT.OUT)
td = .001 #delay between steps
steps = 50  #number of steps x4
for i in range(0,steps):  #CW loop
    MOT.output(12,1)  #first step
    MOT.output(16,0)
    time.sleep(td)
    MOT.output(21,1)
    MOT.output(26,0)  
    time.sleep(td)
    MOT.output(12,0)  #second step
    MOT.output(16,1)
    time.sleep(td)
    MOT.output(21,1)
    MOT.output(26,0)
    time.sleep(td)
    MOT.output(12,0)  #third step
    MOT.output(16,1)
    time.sleep(td)
    MOT.output(21,0)
    MOT.output(26,1)
    time.sleep(td)
    MOT.output(12,1)  #fourth step
    MOT.output(16,0)
    time.sleep(td)
    MOT.output(21,0)
    MOT.output(26,1)
    time.sleep(td)

MOT.output(12,0)  #pause
MOT.output(16,0)
MOT.output(21,0)
MOT.output(26,0)
time.sleep(1)

for i in range(0,50):  #CCW loop
    MOT.output(12,1)  #first step
    MOT.output(16,0)
    time.sleep(td)
    MOT.output(21,0)
    MOT.output(26,1)  
    time.sleep(td)
    MOT.output(12,0)  #second step
    MOT.output(16,1)
    time.sleep(td)
    MOT.output(21,0)
    MOT.output(26,1)
    time.sleep(td)
    MOT.output(12,0)  #third step
    MOT.output(16,1)
    time.sleep(td)
    MOT.output(21,1)
    MOT.output(26,0)
    time.sleep(td)
    MOT.output(12,1)  #fourth step
    MOT.output(16,0)
    time.sleep(td)
    MOT.output(21,1)
    MOT.output(26,0)
    time.sleep(td)
#motor shut down
MOT.output(12,0)
MOT.output(16,0)
MOT.output(21,0)
MOT.output(26,0)

