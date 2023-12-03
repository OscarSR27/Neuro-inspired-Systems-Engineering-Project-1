import cv2
import mediapipe as mp
import time
from google.protobuf.json_format import MessageToDict
from collections import Counter


class handDetector():

    # Initiazisation of the properties of the hand tracking and Mediapipe objects
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5): 
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
    # draw_landmarks function draws the landmarks and transforms the picture to RGB format if a hand is recognized
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        two_hands = False

        if self.results.multi_hand_landmarks:
            # check for two hands
            if len(self.results.multi_hand_landmarks) == 2:
                two_hands=True
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        RightHand1 = False
        # find out which hand was first shown to the system (for later usage to properly count thumb)
        if self.results.multi_handedness:
            for idx, hand_handedness in enumerate(self.results.multi_handedness):
                handedness_dict = MessageToDict(hand_handedness)
            whichHand1 = (handedness_dict['classification'][0]['label'])

            if whichHand1 == "Left":
                RightHand1 = True
            else:
                RightHand1 = False
        return img,two_hands, RightHand1


    # method that loops over a list of landmarks, determines their dimensions, and saves their positions in the lmList
    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList
# function to find the most frequnet number in an array
def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

# main method that sets all the variables, creates a handDetecter instance, and calls the methods to make observations and display count and FPS
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()