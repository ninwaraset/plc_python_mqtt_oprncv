import serial
ser = serial.Serial(port = "COM3", baudrate=57600,bytesize=8,timeout=1, stopbits=serial.STOPBITS_ONE)

while True:

    txt = input("Enter Command : \n")
    ser.write(txt.encode())