# connect loopback on board
import serial
import time

print('You have started the UART loopback utility')
print('Ensure that TX (pin 8) and RX (pin 10) are connected \n')

serialport = serial.Serial("/dev/serial0", baudrate=9600, timeout=3.0)

while True:
    ser_string = raw_input("Type something to transmit over UART: ") # returns string
    serialport.write(ser_string)
    #rcv = serialport.read(len(ser_string))
    rcv = serialport.readline()
    print("String that you sent: " + repr(rcv) + "\n")
    time.sleep(2)
