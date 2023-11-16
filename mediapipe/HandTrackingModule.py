import cv2
import mediapipe as mp
import time
from google.protobuf.json_format import MessageToDict
from collections import Counter


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        two_hands = False

        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) == 2:
                two_hands=True
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        RightHand1 = False
        # RightHand2 = False
        if self.results.multi_handedness:
            for idx, hand_handedness in enumerate(self.results.multi_handedness):
                handedness_dict = MessageToDict(hand_handedness)
            whichHand1 = (handedness_dict['classification'][0]['label'])
            print(whichHand1)

            if whichHand1 == "Left":
                RightHand1 = True
            else:
                RightHand1 = False
            # if two_hands:
            #     whichHand2 = (handedness_dict['classification'][1]['label'])
            #     print(whichHand2)
            #     if whichHand2 == "Left":
            #         RightHand2 = False
            #     else:
            #         RightHand2 = True
            #     return img, two_hands, [RightHand1,RightHand2]

        return img,two_hands, RightHand1

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList

def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]


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