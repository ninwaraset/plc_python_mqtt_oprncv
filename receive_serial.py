import serial
from time import sleep

ser = serial.Serial(port = "COM4", baudrate=57600,bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
while True:
        
        while True:
            if(ser.in_waiting > 0):
                serialString = ser.readline()

                captured_data = serialString.decode('UTF-8')

                print("-------\n Reading : "+captured_data+"\n-------")
                break
            else:
                print("waiting data...")
           
          
            sleep(1)


            