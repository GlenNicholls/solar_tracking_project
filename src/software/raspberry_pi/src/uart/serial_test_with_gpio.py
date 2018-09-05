# connect tx/rx pins to some device. Send data with character ending \n
import serial
import time

print('You have started the UART utility test')
print('Ensure that TX (pin 8) and RX (pin 10) are connected to peripheral device \n')

serialport = serial.Serial("/dev/serial0", baudrate=9600, timeout=3.0)

while True:
    #rcv = serialport.read(len(ser_string))
    rcv = serialport.readline()
    print("String sent: " + repr(rcv) + "\n")
    time.sleep(.25)
