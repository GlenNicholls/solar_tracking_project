import os
import time
import logging

logging.info("Shutdown Invoked. Disabling ports to save power.")


# disable ethernet power
#os.system("cd /usr/hub-ctrl.c")
#os.system("sudo /home/bin/hub-ctrl -h 0 -P 1 -p 0") # turn off ethernet
#os.system("sudo /home/bin/hub-ctrl -h 0 -P 1 -p 1") # turn on ethernet
os.system("sudo /etc/init.d/networking stop")
logging.info("Disabled networking")
time.sleep(10)

# disable HDMI port
# disable = -o | enable = -p
os.system("sudo /opt/vc/bin/tvservice -o")
logging.info("Disabled HDMI port")
time.sleep(10)

# disable usb power
# enable = echo 1 > | disable = echo 0 >
#os.system("echo 0 > /sys/devices/platform/bcm2708_usb/buspower") # this doesn't work and I can't figure out where buspower is located as the cmd above doesn't work right...
#os.system("sudo /home/bin/hub-ctrl -h 0 -P 2 -p 1") # turn on usb ports
os.system("sudo /home/bin/hub-ctrl -h 0 -P 2 -p 0") # turn off usb ports
logging.info("Disabled USB bus power")
time.sleep(10)

# invoke shutdown
os.system("sudo shutdown -h now")
