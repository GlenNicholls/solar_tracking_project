==============================
= SETTING UP UART
==============================
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

==============================
= Python Serial
==============================
  >>> sudo apt-get install python-serial

  Ex: 
    import serial

    serialport = serial.Serial("serial0", baudrate=9600, timeout=3.0)

    while True:
        serialport.write("rnSay something:")
        rcv = port.read(10)
        serialport.write("rnYou sent:" + repr(rcv))