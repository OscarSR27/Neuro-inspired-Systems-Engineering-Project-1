# %%
import numpy as np
import cv2
import time
import os
import HandTrackingModule as htm
from HandTrackingModule import most_frequent
from shared_memory_dict import SharedMemoryDict
from enum import Enum
import time
import socket
import random

# %%
# shared memory for MediaPipe and force sensors
smd = SharedMemoryDict(name='msg', size=1024)
# TODO decide which variables are necessary
smd['signed_number'] = None
smd['pressed_number'] = None

wCam, hCam = 1920, 1080

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

desired_width = 1920
desired_height = 1080

pTime = 0


detector = htm.handDetector(detectionCon=1)

tipIds = [4, 8, 12, 16, 20]
sum = 0
summed_list = []
counter = 0

udp_ip = "192.168.4.1"  # IP del ESP32
#udp_ip = "127.0.0.2" #testing
local_port = 9999  # Puerto local para escuchar
dict={}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', local_port))
# %%
# Define states
class States(Enum):
    READ_INPUT = 0
    ROLE = 1
    READ = 2
    CONFIRM = 3
    WAIT_CONFIRMATION = 4
    
STATE = States.READ_INPUT

# %%

def decode_braille(force_array):
    number = None
    if force_array == "0111":
        number = 0
    elif force_array == "1000":
        number = 1
    elif force_array == "1100":
        number = 2
    elif force_array == "1010":
        number = 3
    elif force_array == "1011":
        number = 4
    elif force_array == "1001":
        number = 5
    elif force_array == "1110":
        number = 6
    elif force_array == "1111":
        number = 7
    elif force_array == "1101":
        number = 8
    elif force_array == "0110":
        number = 9
    else:
        number = -1
        print('Braille pattern not recognized:', force_array)

    return number

def encode_braille(number):
    braille_encoding = {
        0: "0111",
        1: "1000",
        2: "1100",
        3: "1010",
        4: "1011",
        5: "1001",
        6: "1110",
        7: "1111",
        8: "1101",
        9: "0110"
    }

    return braille_encoding.get(number, -1)

def process_hand_detection(img, detector, smd, tipIds, summed_list, counter):
    img, two_hands, right_hand = detector.findHands(img)
    landmarks_list_one = detector.findPosition(img, draw=False)
    sum = 0
    stop_mediapipe = -1
    if two_hands:
        landmarks_list_two = detector.findPosition(img, handNo=1, draw=False)

    if len(landmarks_list_one) != 0:
        fingers_list_one = []

        # Check for thumb
        if right_hand:
            if landmarks_list_one[tipIds[0]][1] < landmarks_list_one[tipIds[0] - 1][1]:
                fingers_list_one.append(1)
            else:
                fingers_list_one.append(0)
        else:
            if landmarks_list_one[tipIds[0]][1] > landmarks_list_one[tipIds[0] - 1][1]:
                fingers_list_one.append(1)
            else:
                fingers_list_one.append(0)


        #Check for 4 fingers
        for id in range(1, 5):
            if landmarks_list_one[tipIds[id]][2] < landmarks_list_one[tipIds[id] - 2][2]:
                fingers_list_one.append(1)
            else:
                fingers_list_one.append(0)

        # Count finger for one hand
        fingers_count_one = np.sum(np.array(fingers_list_one)) #fingers_list_one.count(1)
        print(fingers_count_one)

        if two_hands:
            fingers_list_two = []

            # Check for thumb
            if right_hand:
                if landmarks_list_two[tipIds[0]][1] > landmarks_list_two[tipIds[0] - 1][1]:
                    fingers_list_two.append(1)
                else:
                    fingers_list_two.append(0)
            else:
                if landmarks_list_two[tipIds[0]][1] < landmarks_list_two[tipIds[0] - 1][1]:
                    fingers_list_two.append(1)
                else:
                    fingers_list_two.append(0)

            # Check for 4 fingers
            for id in range(1, 5):
                if landmarks_list_two[tipIds[id]][2] < landmarks_list_two[tipIds[id] - 2][2]:
                    fingers_list_two.append(1)
                else:
                    fingers_list_two.append(0)

            # Count finger for two hand
            fingers_count_two = fingers_list_two.count(1)
            print(fingers_count_two)


        #print sum
        if two_hands:
            sum = fingers_count_one + fingers_count_two
            print(fingers_count_two, fingers_count_one)
        else:
            sum = fingers_count_one
        summed_list.append(sum)
        counter = counter + 1

        if counter >= 15:
            number = most_frequent(summed_list)
            # set shared memory variable
            if smd['signed_number'] == None:
                smd['signed_number'] = number
                print('number sent')
            print("most freq:", number)
            cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
            font_scale = 3
            cv2.putText(img, "Number sent: {} ".format(number), (60, 650), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 128), 1)
            cv2.putText(img,"Get ready to show a new number", (60, 375), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 8)

            cv2.rectangle(img, (1000, 225), (1150, 425), (169, 169, 169), cv2.FILLED)
            if smd['pressed_number'] != None:
                cv2.putText(img, str(smd['pressed_number']), (1040, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
            cv2.putText(img, "Received number:", (935, 175), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)
            
            img_resized = cv2.resize(img, (desired_width, desired_height))
            cv2.imshow("Image", img_resized)
            cv2.rectangle(img, (0, 1920), (0, 1080), (169, 169, 169), cv2.FILLED)
            stop_mediapipe = cv2.waitKey(0)
            #display count inside the frame
            
            ######################################################################
            cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
            cv2.putText(img, str(sum), (60, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
            ######################################################################
            counter = 0
            summed_list = []
    
    return img, summed_list, counter, sum, stop_mediapipe

    # cTime = time.time()
    # fps = 1 / (cTime - pTime)
    # pTime = cTime
    #
    # #display FPS inside the frame
    # cv2.putText(img, f'Frames per second =: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
    #             1, (0, 0, 128), 3)
    
    
#
# %%

stop_mediapipe = -1
role_assigned_flag = False
while True:
    if STATE == States.READ_INPUT:
        success, img = cap.read()
        img, summed_list, counter, sum, stop_mediapipe = process_hand_detection(img, detector, smd, tipIds, summed_list, counter)
        
        # Display the image
        img_resized = cv2.resize(img, (desired_width, desired_height))
        cv2.imshow("Image", img_resized)
        cv2.waitKey(1)
        
        if stop_mediapipe==13:
            stop_mediapipe = -1
            if role_assigned_flag == False:
                role_assigned_flag = True
                STATE = States.ROLE
            else:
                STATE = States.WAIT_CONFIRMATION
                data = encode_braille(sum) + '\0'  #Add null character
                sock.sendto(data.encode(), (udp_ip, local_port))
    if STATE == States.ROLE:
        # Initialize the values
        values = [1, 2]

        # Shuffle the values randomly
        random.shuffle(values)

        # Assign the values to p1 and p2
        p1, p2 = values
        role = str(p1)
        data = encode_braille(p2) + '\0' #Add null character
        sock.sendto(data.encode(), (udp_ip, local_port))
        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
        if role == '1':
            cv2.putText(img, "Sender", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
            STATE = States.READ_INPUT
        if role == '2':
            cv2.putText(img, "Receiver", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
            STATE = States.READ
        img_resized = cv2.resize(img, (desired_width, desired_height))
        cv2.imshow("Image", img_resized)
        cv2.waitKey(2000)
        
    if STATE == States.READ:
        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
        cv2.putText(img, "Waiting message", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
        img_resized = cv2.resize(img, (desired_width, desired_height))
        cv2.imshow("Image", img_resized)
        cv2.waitKey(1000)
        read = 11
        while True:
            data, addr = sock.recvfrom(1024)
            read = decode_braille(data.decode())
            if read != 11:
                break
        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
        cv2.putText(img, "Received: " + str(read), (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
        img_resized = cv2.resize(img, (desired_width, desired_height))
        cv2.imshow("Image", img_resized)
        cv2.waitKey(1000)
        STATE = States.CONFIRM
    if STATE == States.CONFIRM:
        confirm = input("Enter '1' to confirm, '2' to request message again: ")
        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
        cv2.imshow("Image", img_resized)
        print("Confirm: ", confirm, type(confirm))
        if confirm=="1":
            STATE = States.READ_INPUT
            message = "You confirmed"
            data = encode_braille(1) + '\0'  # Agregar carácter nulo
            sock.sendto(data.encode(), (udp_ip, local_port))
        elif confirm=="2":
            STATE = States.READ
            message = "Requesting message again..."
            data = encode_braille(2) + '\0'  # Agregar carácter nulo
            sock.sendto(data.encode(), (udp_ip, local_port))
        else:
            STATE == States.CONFIRM
            message = "Invalid value"
            
        cv2.putText(img, str(message), (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
        img_resized = cv2.resize(img, (desired_width, desired_height))
        cv2.imshow("Image", img_resized)
        cv2.waitKey(1000)
    if STATE == States.WAIT_CONFIRMATION:
        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
        cv2.putText(img, "Waiting confirmation", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
        cv2.imshow("Image", img_resized)
        cv2.waitKey(1000)
        wait_confirm = 11
        while True:
            data, addr = sock.recvfrom(1024)
            wait_confirm = str(decode_braille(data.decode()))
            if wait_confirm != 11:
                break
        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
        cv2.imshow("Image", img_resized)
        if wait_confirm=='1':
            STATE = States.READ
            message = "Receiver confirmed"
        else:
            STATE = States.READ_INPUT
            message = "Receiver is requesting message again"
            
        cv2.putText(img, str(message), (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 8)
        img_resized = cv2.resize(img, (desired_width, desired_height))
        cv2.imshow("Image", img_resized)
        cv2.waitKey(1000)
    
# Cleanup
cap.release()
cv2.destroyAllWindows()

# %%
