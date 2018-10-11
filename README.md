# PV Array Sun Tracking Project
This is the the repository for our solar tracking capstone project.

# Raspberry Pi Setup
To set up the Raspberry pi, perform the following steps after updating:
>>> sudo apt-get update

## Install dependencies
To install dependencies for the python code base and creating egg info for the python interpreter, run the 
following commands, (recommend install in step 1b):

### 1a)
If you would like to develop on the device, run this command to ensure symbolic links point to the source code in this repository.
This allows the developer to make changes here without having to re-install the python repository
>>> sudo python setup.py developer

### 1b)
If you would like to perform a fresh system install, perform this command. This will generate egg info under site-packages, meaning 
src files are copied
>>> sudo python setup.py install
 
## Enable I2C and SPI
Begin by opening a termineal and performing the following steps:
>>> sudo raspi-config

>>> Interfacing Options > I2C > Yes

>>> Interfacing Options > SPI > Yes

>>> sudo reboot

>>> lsmod | grep i2c_

You should now see something come up. You can also do the following to see devices:
>>> sudo i2cdetect -y 1

## Installing avrdude and Configuration
Reference https://learn.adafruit.com/program-an-avr-or-arduino-using-raspberry-pi-gpio-pins/installation

Install AVR dude so that .hex files can be programmed to the uC in charge of the power circuit (recommend install in step 1a).

### 1a) Automatic install

>>> sudo apt-get install avrdude

Verify installation:
>>> avrdude -v

Copy .conf File for Edits

>>> cp /etc/avrdude.conf ~/avrdude_gpio.conf

>>> nano ~/avrdude_gpio.conf

### 1b) Manual install

>>> sudo apt-get install -y build-essential bison flex automake libelf-dev libusb-1.0-0-dev libusb-dev libftdi-dev libftdi1

>>> wget http://download.savannah.gnu.org/releases/avrdude/avrdude-6.1.tar.gz

>>> tar xvfz avrdude-6.1.tar.gz

>>> cd avrdude-6.1

>>> ./configure --enable-linuxgpio

>>> make

>>> sudo make install

Verify installation:
>>> avrdude -v

#### 1a) Automatic configuration
Use the file inside the repository.
Check using this command that you can talk to ATTiny85A:

>>> sudo avrdude -p t84 -C ~/solar_tracking_project/misc_dev/avrdude_gpio.conf -c pi_1 -e -v

#### 1b) Configure avrdude_gpio.conf Manually
Copy .conf File for Edits

>>> cp /usr/local/etc/avrdude.conf ~/avrdude_gpio.conf

>>> nano ~/avrdude_gpio.conf

Append the following to the end of the file:

'''
  # Linux GPIO configuration for avrdude.
  # Change the lines below to the GPIO pins connected to the AVR.
  programmer
    id    = "pi_1";
    desc  = "Use the Linux sysfs interface to bitbang GPIO lines";
    type  = "linuxgpio";
    reset = 23;
    sck   = 17;
    mosi  = 22;
    miso  = 27;
;
'''

#### Verify Output of Command
you should now see something like the following:

'''
  avrdude: Version 6.1, compiled on Oct 10 2018 at 01:07:09                                   
           Copyright (c) 2000-2005 Brian Dean, http://www.bdmicro.com/                        
           Copyright (c) 2007-2014 Joerg Wunsch                                               
                                                                                              
           System wide configuration file is "/home/pi/avrdude_gpio.conf"                     
           User configuration file is "/root/.avrduderc"                                      
           User configuration file does not exist or is not a regular file, skipping          
                                                                                              
           Using Port                    : unknown                                            
           Using Programmer              : pi_1                                               
           AVR Part                      : ATtiny84                                           
           Chip Erase delay              : 4500 us                                            
           PAGEL                         : P00                                                
           BS2                           : P00                                                
           RESET disposition             : possible i/o                                       
           RETRY pulse                   : SCK                                                
           serial program mode           : yes                                                
           parallel program mode         : yes                                                
           Timeout                       : 200                                                
           StabDelay                     : 100                                                
           CmdexeDelay                   : 25                                                 
           SyncLoops                     : 32                                                 
           ByteDelay                     : 0                                                  
           PollIndex                     : 3                                                  
           PollValue                     : 0x53                                               
           Memory Detail                 :                                                    
                                                                                              
                                    Block Poll               Page                       Polled
             Memory Type Mode Delay Size  Indx Paged  Size   Size #Pages MinW  MaxW   ReadBack
             ----------- ---- ----- ----- ---- ------ ------ ---- ------ ----- ----- ---------
             eeprom        65     6     4    0 no        512    4      0  4000  4500 0xff 0xff
             flash         65     6    32    0 yes      8192   64    128  4500  4500 0xff 0xff
             signature      0     0     0    0 no          3    0      0     0     0 0x00 0x00
             lock           0     0     0    0 no          1    0      0  9000  9000 0x00 0x00
             lfuse          0     0     0    0 no          1    0      0  9000  9000 0x00 0x00
             hfuse          0     0     0    0 no          1    0      0  9000  9000 0x00 0x00
             efuse          0     0     0    0 no          1    0      0  9000  9000 0x00 0x00
             calibration    0     0     0    0 no          1    0      0     0     0 0x00 0x00
                                                                                              
           Programmer Type : linuxgpio                                                        
           Description     : Use the Linux sysfs interface to bitbang GPIO lines              
           Pin assignment  : /sys/class/gpio/gpio{n}                                          
             RESET   =  23                                                                    
             SCK     =  17                                                                    
             MOSI    =  22                                                                    
             MISO    =  27                                                                    
                                                                                              
  avrdude: AVR device initialized and ready to accept instructions                            
                                                                                              
  Reading | ################################################## | 100% 0.00s                   
                                                                                              
  avrdude: Device signature = 0x1e930c                                                        
  avrdude: safemode: lfuse reads as 62                                                        
  avrdude: safemode: hfuse reads as DF                                                        
  avrdude: safemode: efuse reads as FF                                                        
  avrdude: erasing chip                                                                       
                                                                                              
  avrdude: safemode: lfuse reads as 62                                                        
  avrdude: safemode: hfuse reads as DF                                                        
  avrdude: safemode: efuse reads as FF                                                        
  avrdude: safemode: Fuses OK (E:FF, H:DF, L:62)                                              
                                                                                              
  avrdude done.  Thank you.                                                                   
'''

No further configuration is required.


# TODO:
* Install new caps based on ACS712 NF. We will be doing less than 1k samples per second for current measurements, so we should prioritize lower NF
* Set up software for the DS3231 package, dynamic control based on WIFI to synchronize RTC and/or switch to RTC for timekeeping
* Logging/database
* voltage sense for panel, load, pi, battery (for safe shutdown)
* setup script to configure system entirely along with reboot schemes where required (don't want set up anything noted below in the other sections)
* unit test/regression test framework
* Circuit for the power/timer: https://www.allaboutcircuits.com/projects/build-programmable-time-based-switches-using-a-real-time-clock/
* High level web server for simple control
* SW alg from Josh/Brad for the light sensors
* SW for the motor control from Mike
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
