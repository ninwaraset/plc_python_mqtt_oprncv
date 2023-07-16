import serial
from time import sleep
import paho.mqtt.client as mqtt
ser = serial.Serial(port = "COM7", baudrate=57600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)


import cv2
import numpy as np
#import time

cap = cv2.VideoCapture(1)


def check_CAM():

    # width = 0



    while True:
        #cap = cv2.VideoCapture(1)
        Width_Detect = 284
        Height_Detect = 281
        err_box  = 20
        width =0
        ret, frame = cap.read()
        roi = frame[:700,0:700]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) == 4:
                
                x, y, width, height = cv2.boundingRect(approx)
                print("Cup dimensions:")
                print("Width:", width)
                print("Height:", height)
                cv2.drawContours(roi, [approx], -1, (0, 255, 0), 2)
                cv2.rectangle(roi, (x, y), (x + width, y + height), (0, 0, 255), 2)
        #cv2.imshow('Detected Cup', roi)
        if (Width_Detect - err_box) <= width <= (Width_Detect + err_box) and (Height_Detect - err_box) <= height <= (Height_Detect + err_box):
            # print("Yes")
            
            # received_message = "CD"
            # break
            #cap.release()
            cv2.destroyAllWindows()
            return 1
        else:
            # print("No")
            
            # received_message = "CD"
            # break
            #cap.release()
            cv2.destroyAllWindows()
            return 0
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
            
    cap.release()
    cv2.destroyAllWindows()














topic_mqtt = "python_plc"
received_message = ""

# Callback function for connection event
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribe to the topic(s) after successful connection
    client.subscribe(topic_mqtt)

# Callback function for message arrival
def on_message(client, userdata, msg):
    global received_message
    received_message = msg.payload.decode()
    # print("Received message: " + received_message)
    # Process the received message as needed

# Create a client instance
client = mqtt.Client()

# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Set the credentials
username = "ailas"
password = "ailas"
client.username_pw_set(username, password)

# Connect to the MQTT broker
broker_address = "13.229.98.224"
port = 1883
client.connect(broker_address, port)

# Start the MQTT loop in a separate thread
client.loop_start()
couter_call_data = 0 
while 1:
    
    # couter_call_data +=1
    # print(couter_call_data)
    # if couter_call_data == 50 :
    #     received_message = "TT"
    #     couter_call_data =0
    
    txt = received_message 
    
    
    if txt != '':
        print("-------------------------")
        print("command to PLC : " +  txt)
        ser.write(txt.encode())
        print("-------------------------")
        
    else :
        couter_call_data +=1
        # print(couter_call_data)
        if couter_call_data == 50 :
            txt = "TT"
            print("-------------------------")
            print("command to PLC : " +  txt)
            ser.write(txt.encode())
            print("-------------------------")
            couter_call_data =0
            

    
    received_message = ''

    
    if txt == "TT":
        
        
        couter_round = 0
        while(1):
            sleep(0.5)
            if(ser.in_waiting > 0):
                serialData = ser.readline()
                print(serialData)
                head = serialData[0:2].decode()
                # tail = serialData[-2:].decode()
                print("HEAD : "+str(head))
                # print("tail : "+str(tail) )
                
                if head == "EA" :
                    captured_data = serialData[2:4]
                    captured_data_1 = serialData[4:6]
                    captured_data_2 = serialData[6:8]
                    captured_data_3 = serialData[8:10]
                    # print(captured_data)
                    # print(captured_data[0:2].hex(sep=' '))
                    int_val_0 = int.from_bytes(captured_data[0:2], "little", signed="True")
                    int_val_1 = int.from_bytes(captured_data_1[0:2], "little", signed="True")
                    int_val_2 = int.from_bytes(captured_data_2[0:2], "little", signed="True")
                    int_val_3 = int.from_bytes(captured_data_3[0:2], "little", signed="True")
                    print("input             : "+ str(int_val_0) + " ea.")
                    print('output            : '+ str(int_val_1) + ' ea.')
                    print('output "BLUE"     : '+ str(int_val_2) + ' ea.')
                    print('output "NOT BLUE" : '+ str(int_val_3) + ' ea.')
                    print("----------------------------------------------------------")
                    client.publish(topic_mqtt+"/0",int_val_0)
                    client.publish(topic_mqtt+"/1",int_val_1)
                    client.publish(topic_mqtt+"/2",int_val_2)
                    client.publish(topic_mqtt+"/3",int_val_3)
                    # print("Reading : "+captured_data)
                    client.publish(topic_mqtt+"/camera",0)
                    sleep(0.5)
                    break
                elif head == "CP" :
                    camera_confirm = check_CAM()
                    # camera_confirm = input("openCV detect : ")
                    # sleep(2)
                    # camera_confirm = "1"
                    print(camera_confirm)
                    if camera_confirm == 1 :
                        
                        ser.write("OK".encode())
                        print("use ok")
                    else :
                        ser.write("NO".encode())
                        print("use no")

                    sleep(5)

                    client.publish(topic_mqtt+"/camera",1)
                    
                    sleep(0.5)
                    break
                else :
                    client.publish(topic_mqtt+"/camera",0)
                    break
            else:
                print("waiting data...")
                couter_round += 1
            if couter_round  >= 1:
                break
            



