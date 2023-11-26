import numpy as np
import cv2
import random
import time
import os
import pandas as pd
import HandTrackingModule as htm
from HandTrackingModule import most_frequent
from shared_memory_dict import SharedMemoryDict

# Experiment details
subject_id = 5      # change it for every participant
sample_array = [5, 10, 15, 20]
sample_array = random.sample(sample_array, len(sample_array))
time_duration = 120    # This is the time for running one experiment

#loop through every sample value for each participant
for i in range(len(sample_array)):
    # # shared memory for MediaPipe and force sensors
    # smd = SharedMemoryDict(name='msg', size=1024)
    # # TODO decide which variables are necessary
    # smd['signed_number'] = None
    # smd['pressed_number'] = None

    wCam, hCam = 1920, 1080

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)


    detector = htm.handDetector(detectionCon=1)

    tipIds = [4, 8, 12, 16, 20]
    sum = 0
    summed_list = []
    samples = 0
    sending_counter = 0

    true_numbers = np.random.randint(10, size=600)
    signed_numbers = np.zeros_like(true_numbers)
    start_time = time.time()  # Start recording time


    while True:
        success, img = cap.read()
        img, two_hands, right_hand = detector.findHands(img)
        landmarks_list_one = detector.findPosition(img, draw=False)
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


            if two_hands:
                sum = fingers_count_one + fingers_count_two
            else:
                sum = fingers_count_one
            summed_list.append(sum)
            samples = samples + 1

            if samples >= sample_array[i]:
                number = most_frequent(summed_list)
                signed_numbers[sending_counter] = number
                # # set shared memory variable
                # if smd['signed_number'] == None:
                #     smd['signed_number'] = number
                #     print('number sent')
                cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
                cv2.putText(img, "Number sent: {} ".format(number), (60, 650), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 128), 8)
                cv2.putText(img,"Get ready to show a new number", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 8)
                cv2.imshow("Image", img)
                cv2.rectangle(img, (0, 1920), (0, 1080), (169, 169, 169), cv2.FILLED)
                cv2.waitKey(0)
                samples = 0
                summed_list = []
                # if sending_counter == len(true_numbers)-1: #if all n numbers have been collected
                print(time.time() - start_time)
                if time.time() - start_time >= time_duration:
                    signed_numbers[sending_counter] = number
                    experiment_details_path = os.path.join("..", "Experiment_data", "subject_id{}_sample_size{}.csv".format(subject_id,sample_array[i]))
                    cut_idx = sending_counter + 1
                    true_numbers = true_numbers[0:cut_idx]
                    signed_numbers = signed_numbers[0:cut_idx]
                    dict = {"ground_truth": true_numbers, "response": signed_numbers}
                    # np.save(experiment_details_path, dict)
                    df = pd.DataFrame(dict)
                    df.to_csv(experiment_details_path, index = False)

                    if len(sample_array) == (i+1):
                        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
                        cv2.putText(img, "recording participant {} finished".format(subject_id), (60, 375),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 8)
                        cv2.putText(img, "press enter to quit", (60, 500), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 169), 8)
                        cv2.imshow("Image", img)
                        cv2.rectangle(img, (0, 1920), (0, 1080), (169, 169, 169), cv2.FILLED)
                        cv2.waitKey(0)

                        break
                    else:
                        cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
                        cv2.putText(img, "Press enter to start a new recording with {} samples".format(sample_array[i+1])
                                    , (60, 375), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 0),8)
                        cv2.imshow("Image", img)
                        cv2.rectangle(img, (0, 1920), (0, 1080), (169, 169, 169), cv2.FILLED)
                        cv2.waitKey(0)
                        break
                else:
                    signed_numbers[sending_counter] = number
                    sending_counter = sending_counter + 1


        #display count inside the frame
        cv2.rectangle(img, (20, 225), (170, 425), (169, 169, 169), cv2.FILLED)
        cv2.putText(img, str(sum), (60, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
        cv2.putText(img, "current detection", (50, 175), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

        cv2.rectangle(img, (1000, 225), (1150, 425), (169, 169, 169), cv2.FILLED)
        cv2.putText(img, str(true_numbers[sending_counter]), (1040, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
        cv2.putText(img, "Sign:", (1035, 175), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)

        # cTime = time.time()
        # fps = 1 / (cTime - pTime)
        # pTime = cTime
        #
        # #display FPS inside the frame
        cv2.putText(img, f'second =: {int(time.time() - start_time)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 128), 3)

        cv2.imshow("Image", img)

        if cv2.waitKey(1) == 13:
            break

        cv2.waitKey(1)

        # if time.time() - start_time > time_duration:    # break out of loop if 2 minutes have passed
        #     break

    # dict = {"True numbers": true_numbers, "Signed Numbers": signed_numbers}
    # np.save(experiment_details, dict)