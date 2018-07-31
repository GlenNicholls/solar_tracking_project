import os
import time
import logging

# TODO: find good logging system for this 
logging.info("System Setup Has Begun!")

# Make #~/home/bin dir for scripts in user PATH
os.system("sudo mkdir ~/home/bin")
logging.info("Created #~/home/bin dir for user scripts visible in $PATH")
time.sleep(1)

# Acquire sys update & upgrade
os.system("sudo apt-get update")
os.system("sudo apt-get upgrade")
logging.info("Installed all updates and upgrade")
time.sleep(1)

# Install libusb
os.system("sudo apt-get install libusb-dev")
logging.info("Installed libusb")
time.sleep(1)

# Install minicom
os.system("sudo apt-get install minicom")
# cd /boot
# ls -l cmdline.txt
# sudo cp cmdline.txt cmdline.txt.backup
# after copy, delete ttyAMA0 reference
# cd /etc
# sudo cp inittab.txt inittab.txt.backup
# comment line with ttyAMA0
# echo 8 > /dev/ttyAMA0 to send 8 to uart device
logging.info("Installed minicom")
time.sleep(1)

# USB hub ctrl
# TODO: fix this to clone sub-repo into our repo.
os.system("sudo git clone https://github.com/codazoda/hub-ctrl.c /usr/")
os.system("cd /usr/hub-ctrl.c")
os.system("gcc -o hub-ctrl hub-ctrl.c -lusb")
os.system("sudo cp hub-ctrl /home/bin/")
logging.info("Installed and compiled USB control")
time.sleep(1)




