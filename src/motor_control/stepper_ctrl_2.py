import RPi.GPIO as MOT
import time
MOT.setwarnings(False)
MOT.setmode(MOT.BCM)
lines = [12,13,16,19,26]
for pin in lines:  #sets pins 12,13,16,19,26 as outputs
    MOT.setup(pin,MOT.OUT)
# Pin assignment: 12-direction (17), 13-EL controller enable (10), 16-clock (18)
# 19-AZ controller enable (10), 26-reset (20)
#time.sleep(10)
ctl = 0
cnt = 0
dir = 1
MOT.output(16,1)  #sets clock pin high, falling edge
MOT.output(12,dir)  #sets motor direction 1 = W/N, 0 = E/S
MOT.output(13,0)  #disable EL controller
MOT.output(19,0)  #disable AZ contyroller
MOT.output(26,1)  #resets to starting configuration 1010
MOT.output(26,0)  #starts reset
MOT.output(26,1)  #ends reset
MOT.output(19,1)  #enable AZ  controller
MOT.output(13,1) #enable EL controller
td = .005  #controls the number of steps
steps = 72  #sets number of steps (72 = 1 degree elevation) (22 = 1 degree azimuth)
for clk in range(0,steps):  #run number of steps
    cnt = cnt+1
    if cnt == 22:
        MOT.output(19,0) #disables az controller
    MOT.output(16,0)  #pulse the clock pin                         
    time.sleep(td)
    MOT.output(16,1)
    time.sleep(td)
MOT.output(19,0)  #disable az controller
MOT.output(13,0)  #disable el controller
cnt = 0
