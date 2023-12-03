# %%
import numpy as np
import cv2
import time
import os
import HandTrackingModule as htm
from HandTrackingModule import most_frequent
from shared_memory_dict import SharedMemoryDict

# %%
# shared memory for MediaPipe and force sensors
smd = SharedMemoryDict(name='msg', size=1024)
# TODO decide which variables are necessary
smd['signed_number'] = None
smd['pressed_number'] = None

#set resolution for different diplay resolutions
wCam, hCam = 1920, 1080 

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=1)

tipIds = [4, 8, 12, 16, 20]
#sum the extended fingers
sum = 0
#collect the samples in the summed_list and later take the most frequent instance of the array
summed_list = []
#samples that have been already collected
samples = 0

# while loop for continuous detection, which terminates when enter key is pressed, i.e., 13 in ASCII
while True:
    # capture the image
    success, img = cap.read()
    # findHands method to detect hand and track landmarks
    img, two_hands, right_hand = detector.findHands(img)
    # findPosition method on it to obtain a list of landmarks
    landmarks_list_one = detector.findPosition(img, draw=False)
    # if two hands are in the frame obtain a list of landmarks for second hand
    if two_hands:
        landmarks_list_two = detector.findPosition(img, handNo=1, draw=False)

    # If landmarks are detected in the selected frame thus one or two hands are in the frame, then create a fingers_list list
    if len(landmarks_list_one) != 0:
        fingers_list_one = []

        # Check for thumb
        # If the thumb is horizontally extended append one else a zero to finger_list_one
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
        # if the fingers are vertically extended append a one else a zero to finger_list_one
        for id in range(1, 5):
            if landmarks_list_one[tipIds[id]][2] < landmarks_list_one[tipIds[id] - 2][2]:
                fingers_list_one.append(1)
            else:
                fingers_list_one.append(0)

        # Count finger for one hand
        fingers_count_one = np.sum(np.array(fingers_list_one)) 

    # in case of tow hands check the same for the second hand
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


        #print sum
        if two_hands:
            sum = fingers_count_one + fingers_count_two # sum both hands
        else:
            sum = fingers_count_one # sum one hand only
        samples = samples + 1

    # sample size set to 15 since Mediapipe experimental results showed that this will give the best ITR:
        if samples >= 15:
            # find the most frequent number in the samples array (summed_list)
            number = most_frequent(summed_list)
            # set shared memory variable
            if smd['signed_number'] == None:
                smd['signed_number'] = number
            # display sending screen
            cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
            cv2.putText(img, "Number sent: {} ".format(number), (60, 650), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 128), 8)
            cv2.putText(img,"Get ready to show a new number", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 8)

            cv2.rectangle(img, (1000, 225), (1150, 425), (169, 169, 169), cv2.FILLED)
            if smd['pressed_number'] != None:
                cv2.putText(img, str(smd['pressed_number']), (1040, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
            cv2.putText(img, "Received number:", (935, 175), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

            cv2.imshow("Image", img)
            cv2.rectangle(img, (0, 1920), (0, 1080), (169, 169, 169), cv2.FILLED)
            cv2.waitKey(0)
            #reset values
            samples = 0
            summed_list = []


    #display count inside the frame
    cv2.rectangle(img, (20, 225), (170, 425), (169, 169, 169), cv2.FILLED)
    cv2.putText(img, str(sum), (60, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)

    #display resived number inside the frame
    cv2.rectangle(img, (1000, 225), (1150, 425), (169, 169, 169), cv2.FILLED)
    if smd['pressed_number'] != None:
        cv2.putText(img, str(smd['pressed_number']), (1040, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
    cv2.putText(img, "Received number:", (935, 175), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

    cv2.imshow("Image", img)

    if cv2.waitKey(1) == 13:
        break

    cv2.waitKey(1)