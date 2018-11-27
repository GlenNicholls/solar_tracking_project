# PV Array Sun Tracking Project
This is the the repository for our solar tracking capstone project.

# Raspberry Pi Setup
To set up the Raspberry pi, perform the following steps after updating:

    sudo apt-get update

# Install Pandas
The pandas package in setuptools with `pip install` is not the recommend method, so install manually using the following
on a linux based system:

    sudo apt-get install python-pandas

# Install dependencies
To install dependencies for the python code base and creating egg info for the python interpreter, run the 
following commands, (recommend install in step 1b):

## 1a)
If you would like to develop on the device, run this command to ensure symbolic links point to the source code in this repository.
This allows the developer to make changes here without having to re-install the python repository

    sudo python setup.py develop

## 1b)
If you would like to perform a fresh system install, perform this command. This will generate egg info under site-packages, meaning 
src files are copied

    sudo python setup.py install
    
# Enable I2C and SPI
Begin by opening a termineal and performing the following steps:

    sudo raspi-config
    
    Interfacing Options > I2C > Yes
    
    Interfacing Options > SPI > Yes
    
    sudo reboot
    
    lsmod | grep i2c_

You should now see something come up. You can also do the following to see devices:

    sudo i2cdetect -y 1

You should only see a single I2C device at address `0x68`

         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- --
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
    70: -- -- -- -- -- -- -- --

# Installing avrdude
Reference https://learn.adafruit.com/program-an-avr-or-arduino-using-raspberry-pi-gpio-pins/installation

NOTE: If the uC is swapped or the pins are changed from those delivered with the schematic, the `Makefile`
along with the programmer `pi_1` in the `avrdude_gpio.conf` file will need to be adjusted.

## 1) Install AVR toolchain:
    
    sudo apt-get install gcc-avr binutils-avr avr-libc

Install AVR dude so that .hex files can be programmed to the uC in charge of the power circuit (recommend install in step 1a).

## 2) Automatic install of AVRDude

    sudo apt-get install avrdude

## 3) Verify installation:

    avrdude -v

You should see an output similar to this:

    avrdude: Version 6.1, compiled on Oct 10 2018 at 01:07:09
         Copyright (c) 2000-2005 Brian Dean, http://www.bdmicro.com/
         Copyright (c) 2007-2014 Joerg Wunsch

         System wide configuration file is "/usr/local/etc/avrdude.conf"
         User configuration file is "/home/pi/.avrduderc"
         User configuration file does not exist or is not a regular file, skipping


    avrdude: no programmer has been specified on the command line or the config file
         Specify a programmer using the -c option and try again

## 4) Check wiring of programming wires and the clock fuses of device
Check using this command that you can talk to ATTiny85A:

    cd dev/

    sudo avrdude -p t84 -C avrdude_gpio.conf -c pi_hat -e -v

If this does not work, double check that the pins used below match the Pi's BCM pin numbers. Double check schematic
and wiring as well:


    # Linux GPIO configuration for avrdude.
    # Change the lines below to the GPIO pins connected to the AVR.
    programmer
        id    = "pi_hat";
        desc  = "Use the Linux sysfs interface to bitbang GPIO lines";
        type  = "linuxgpio";
        reset = 23;
        sck   = 17;
        mosi  = 22;
        miso  = 27;
    ;

When it works, you should now see something like the following:

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

## 5) Build a clean .hex file and load it to the device

    cd misc_dev/

    make clean

    make install

Make sure that you see a similar success reported like so:

    avrdude: AVR device initialized and ready to accept instructions
    
    Reading | ################################################## | 100% 0.00s
    
    avrdude: Device signature = 0x1e930c
    avrdude: safemode: lfuse reads as 62
    avrdude: safemode: hfuse reads as DF
    avrdude: safemode: efuse reads as FF
    avrdude: NOTE: "flash" memory has been specified, an erase cycle will be performed
             To disable this feature, specify the -D option.
    avrdude: erasing chip
    avrdude: reading input file "blinky.hex"
    avrdude: input file blinky.hex auto detected as Intel Hex
    avrdude: writing flash (68 bytes):
    
    Writing | ################################################## | 100% 0.13s
    
    avrdude: 68 bytes of flash written
    avrdude: verifying flash memory against blinky.hex:
    avrdude: load data flash data from input file blinky.hex:
    avrdude: input file blinky.hex auto detected as Intel Hex
    avrdude: input file blinky.hex contains 68 bytes
    avrdude: reading on-chip flash data:
    
    Reading | ################################################## | 100% 0.10s
    
    avrdude: verifying ...
    avrdude: 68 bytes of flash verified
    
    avrdude: safemode: lfuse reads as 62
    avrdude: safemode: hfuse reads as DF
    avrdude: safemode: efuse reads as FF
    avrdude: safemode: Fuses OK (E:FF, H:DF, L:62)
    
    avrdude done.  Thank you.

The board is now programmed.


# Final Test TBD
Connect the Raspberry Pi to the provided pi hat expansion along with wiring the unit. Run the following to test the system:

    cd ~/solar_tracking_project

    sudo python setup.py test

After the tests have passed, no further configuration is required and the system is ready
