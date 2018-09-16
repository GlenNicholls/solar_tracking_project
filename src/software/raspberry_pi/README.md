# Raspberry Pi Setup
To set up the Raspberry pi, perform the following steps

## Install dependencies
To install dependencies for the python code base and creating egg info for the python interpreter, run the 
following commands, (recommend install in step 2b):

### 1)
>>> cd ~/solar_tracking_project/src/software/raspberry_pi/src/

### 2a)
If you would like to develop on the device, run this command to ensure symbolic links point to the source code in this repository.
This allows the developer to make changes here without having to re-install the python repository
>>> sudo python setup.py developer

### 2b)
If you would like to perform a fresh system install, perform this command. This will generate egg info under site-packages, meaning 
src files are copied
>>> sudo python setup.py install
 
# TODO:
* Set up software for the DS3231 package, dynamic control based on WIFI to synchronize RTC and/or switch to RTC for timekeeping
* Logging/database
* voltage sense
* Circuit for the power/timer: https://www.allaboutcircuits.com/projects/build-programmable-time-based-switches-using-a-real-time-clock/
* High level web server to simple control
* SW from Graeme for SE's
* SW alg from Josh/Brad for the light sensors
* SW for the motor control
* pulling information from web regarding sun position



# Ignore the below
# Setting Up UART
For setting up UART on pi zeroW to forward to pins 8(TXD) & 10(RXD)

REFERENCE: https://raspberrypi.stackexchange.com/questions/45570/how-do-i-make-serial-work-on-the-raspberry-pi3-pi3b-pizerow

  >>> systemctl disable bluetooth.service # TODO: figure out if this cmd in script can reduce steps below
  >>> sudo systemctl stop serial-getty@ttyS0.service
  >>> sudo systemctl disable serial-getty@ttyS0.service

  1) to view information about settings:
    * cat /boot/overlays/README
  2) Enable serial
    * TODO: figure out how to do this via cmd line
  3) Disable bluetooth
    * >>> sudo vi /boot/config.txt
    * Change to dtoverlay=pi3-disable_bt, this disables bluetooth.
  4) reboot system
    * >>> sudo reboot
  5) Serial console
    - choose a, b, c. a is preferred
    a) enable hardware serial console
      * >>> sudo raspi-config
      * navigate to Interfacing Options>Serial
      * Select [No] for the Serial console
      * Select [Yes] for the Serial Port Hardware Enabled
    b) disable serial console
      * >>> sudo vi /boot/cmdline.txt
      * remove the word phase "console=serial0,115200" or "console=ttyAMA0,115200"
      * save changes and exit
    c) enable serial console
      * >>> sudo vi /boot/cmdline.txt
      * Change file to following:
      * dwc_otg.lpm_enable=0 console=tty1 console=serial0(or ttyAMA0),115200 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
      * save changes and exit
  7) Enable UART
    * >>> sudo vi /boot/config.txt
    * if not already, add/change core_freq=250
    * enable_uart=1
  8) reboot system
    * >>> sudo reboot


# Setting Up Python Serial
  >>> sudo apt-get install python-serial

  Ex: 
    import serial

    serialport = serial.Serial("serial0", baudrate=9600, timeout=3.0)

    while True:
        serialport.write("rnSay something:")
        rcv = port.read(10)
        serialport.write("rnYou sent:" + repr(rcv))
