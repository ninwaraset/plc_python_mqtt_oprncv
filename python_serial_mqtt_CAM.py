import serial
from time import sleep
import paho.mqtt.client as mqtt


ser = serial.Serial(port = "COM7", baudrate=57600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)


import cv2
import numpy as np
#import time

cap = cv2.VideoCapture(1)


def check_CAM():

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


couter_call_data = 0 #set variable timer for count time to received msg from plc
while 1: #loop 
    
    txt = received_message #keep variable form mqtt

    if txt != '': #if received cmd msg from mqtt

        print("-------------------------")
        print("command to PLC : " +  txt)
        ser.write(txt.encode()) #sent msg to plc
        print("-------------------------")
        
    else : #if not received cmd msg from mqtt
        couter_call_data +=1  #count time
        if couter_call_data == 50 : #if timer complate
            txt = "TT" # set cmd msg sent to plc for want to receive msg form plc
            print("-------------------------")
            print("command to PLC : " +  txt)
            ser.write(txt.encode()) #sent msg to plc
            print("-------------------------")
            couter_call_data =0 #reset timer
            
    received_message = '' #reset variable form mqtt

    
    if txt == "TT":  #if sent cmd msg to receive msg form plc
        
        couter_round = 0
        while(1):
            sleep(0.5) # sleep wait 0.5 sec
            if(ser.in_waiting > 0): # if dont have msg receive form plc in time
                serialData = ser.readline() #receive msg form plc 
                print(serialData)
                head = serialData[0:2].decode()  #keep head byte form msg
                print("HEAD : "+str(head))
                
                if head == "EA" : #check head 
                    captured_data = serialData[2:4] #keep data form msg
                    captured_data_1 = serialData[4:6] #keep data form msg
                    captured_data_2 = serialData[6:8] #keep data form msg
                    captured_data_3 = serialData[8:10] #keep data form msg
                    int_val_0 = int.from_bytes(captured_data[0:2], "little", signed="True") #tranfrom byte to int
                    int_val_1 = int.from_bytes(captured_data_1[0:2], "little", signed="True")
                    int_val_2 = int.from_bytes(captured_data_2[0:2], "little", signed="True")
                    int_val_3 = int.from_bytes(captured_data_3[0:2], "little", signed="True")
                    print("input             : "+ str(int_val_0) + " ea.")
                    print('output            : '+ str(int_val_1) + ' ea.')
                    print('output "BLUE"     : '+ str(int_val_2) + ' ea.')
                    print('output "NOT BLUE" : '+ str(int_val_3) + ' ea.')
                    print("----------------------------------------------------------")
                    client.publish(topic_mqtt+"/0",int_val_0) #sent mqtt msg in topic ..../0
                    client.publish(topic_mqtt+"/1",int_val_1)
                    client.publish(topic_mqtt+"/2",int_val_2)
                    client.publish(topic_mqtt+"/3",int_val_3)
                    client.publish(topic_mqtt+"/camera",0)
                    sleep(0.5)
                    break
                elif head == "CP" : #check head 
                    camera_confirm = check_CAM() #call function opencv and set check variable

                    print(camera_confirm)
                    if camera_confirm == 1 : # if check opencv passs 
                        ser.write("OK".encode()) #sent result opencv msg to plc 
                        print("use ok")
                    else : # if check opencv not passs 
                        ser.write("NO".encode())#sent result opencv msg to plc 
                        print("use no")
                    sleep(5)

                    client.publish(topic_mqtt+"/camera",1) 
                    
                    sleep(0.5)
                    break
                else :  #for what???
                    client.publish(topic_mqtt+"/camera",0)
                    break
            else: # if dont have msg receive form plc in time
                print("waiting data...")
                couter_round += 1

            if couter_round  >= 1: #for what???
                break
            



