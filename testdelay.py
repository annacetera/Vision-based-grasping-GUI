import serial
import time

(serial.Serial('COM6', 115200)).write(str.encode('6'))
# def test(ard):
#     ard.write(str.encode('6'))
#     print(5)e
# test(ard)
