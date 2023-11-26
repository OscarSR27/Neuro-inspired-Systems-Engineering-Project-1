import numpy as np
import cv2
import time
import os
import HandTrackingModule as htm
from HandTrackingModule import most_frequent
from shared_memory_dict import SharedMemoryDict

# Experiment details
subject_id = 0      # change it for every participant
sample_array = [5, 10, 15, 20]
#loop through every sample value for each participant
for i in range(len(sample_array)):
    # shared memory for MediaPipe and force sensors
    smd = SharedMemoryDict(name='msg', size=1024)
    # TODO decide which variables are necessary
    smd['signed_number'] = None
    smd['pressed_number'] = None

    wCam, hCam = 1920, 1080

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    pTime = 0


    detector = htm.handDetector(detectionCon=1)

    tipIds = [4, 8, 12, 16, 20]
    sum = 0
    summed_list = []
    samples = 0
    sending_counter = 0

    true_numbers = np.random.randint(10, size=2)
    signed_numbers = np.zeros_like(true_numbers)

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
            samples = samples + 1

            if samples >= 20:
                number = most_frequent(summed_list)
                signed_numbers[sending_counter] = number
                # set shared memory variable
                if smd['signed_number'] == None:
                    smd['signed_number'] = number
                    print('number sent')
                print("most freq:", number)
                cv2.rectangle(img, (0, 0), (1920, 1080), (169, 169, 169), cv2.FILLED)
                cv2.putText(img, "Number sent: {} ".format(number), (60, 650), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 128), 8)
                cv2.putText(img,"Get ready to show a new number", (60, 375), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 8)
                cv2.imshow("Image", img)
                cv2.rectangle(img, (0, 1920), (0, 1080), (169, 169, 169), cv2.FILLED)
                cv2.waitKey(0)
                samples = 0
                summed_list = []
                if sending_counter == 1: #if all n numbers have been collected
                    signed_numbers[sending_counter] = number
                    experiment_details_path = os.path.join("..", "Experiment_data", "subject_id{}_sample_size{}".format(subject_id,sample_array[i]))
                    dict = {"True numbers": true_numbers, "Signed Numbers": signed_numbers}
                    np.save(experiment_details_path, dict)

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

        cv2.rectangle(img, (1000, 225), (1150, 425), (169, 169, 169), cv2.FILLED)
        cv2.putText(img, str(true_numbers[sending_counter]), (1040, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)

        # cTime = time.time()
        # fps = 1 / (cTime - pTime)
        # pTime = cTime
        #
        # #display FPS inside the frame
        # cv2.putText(img, f'Frames per second =: {int(fps)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
        #             1, (0, 0, 128), 3)

        cv2.imshow("Image", img)

        if cv2.waitKey(1) == 13:
            break

        cv2.waitKey(1)

    print(signed_numbers)
    # dict = {"True numbers": true_numbers, "Signed Numbers": signed_numbers}
    # np.save(experiment_details, dict)

























# import cv2
# import time
# import os
# import HandTrackingModule as htm
#
# # Set up the camera
# wCam, hCam = 1920, 1080
# cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)
#
# # Create a hand detector object
# detector = htm.handDetector(detectionCon=1)
#
# # Initialize finger tip IDs for the left and right hands
# left_tip_ids = [4, 8, 12, 16, 20]
# right_tip_ids = [4 + 21, 8 + 21, 12 + 21, 16 + 21, 20 + 21]
#
# while True:
#     success, img = cap.read()
#
#     # Find landmarks for both hands
#     img = detector.findHands(img)
#     landmarks_list = detector.findPosition(img, draw=False)
#     print("Length of landmark list: ", len(landmarks_list))
#
#     if len(landmarks_list) >= 21:  # Ensure there are enough landmarks for both hands
#         # Initialize finger count lists for both hands
#         left_fingers = [0, 0, 0, 0, 0]
#         right_fingers = [0, 0, 0, 0, 0]
#
#         # Count fingers for the left hand
#         for id in range(5):
#             if landmarks_list[left_tip_ids[id]][1] > landmarks_list[left_tip_ids[id] - 1][1]:
#                 left_fingers[id] = 1  # Left finger is open
#                 print("Length of landmark test: ", len(landmarks_list))
#
#         # Count fingers for the right hand
#         for id in range(5):
#             if landmarks_list[right_tip_ids[id]][1] > landmarks_list[right_tip_ids[id] - 1][1]:
#                 right_fingers[id] = 1  # Right finger is open
#
#         # Calculate the total finger count for both hands
#         total_fingers = sum(left_fingers) + sum(right_fingers)
#
#         # Display finger count inside the frame
#         cv2.rectangle(img, (20, 225), (170, 425), (169, 169, 169), cv2.FILLED)
#         cv2.putText(img, str(total_fingers), (60, 375), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 128), 20)
#
#     # Display the frame
#     cv2.imshow("Image", img)
#
#     # Exit the loop when the Enter key is pressed
#     if cv2.waitKey(1) == 13:
#         break
#
# # Release the camera and close OpenCV windows
# cap.release()
# cv2.destroyAllWindows()
