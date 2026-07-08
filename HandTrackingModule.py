import cv2
import mediapipe as mp


class HandDetector:

    def __init__(self,
                 mode=False,
                 maxHands=2,
                 detectionCon=0.5,
                 trackCon=0.5):

        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.previousLmList = []
        self.smoothFactor = 0.7

        self.mpHands = mp.solutions.hands

        self.hands = self.mpHands.Hands(
            static_image_mode=mode,
            max_num_hands=maxHands,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )

        self.mpDraw = mp.solutions.drawing_utils

        self.results = None
        self.lmList = []
        self.handType = None

        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.results = self.hands.process(rgb)

        if self.results.multi_hand_landmarks:

            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(
                        img,
                        handLms,
                        self.mpHands.HAND_CONNECTIONS
                    )

        return img

    def findPosition(self, img, handNo=0):

        oldLmList = self.lmList.copy()

        self.lmList = []

        if self.results.multi_hand_landmarks:

            myHand = self.results.multi_hand_landmarks[handNo]

            h, w, c = img.shape

            for id, lm in enumerate(myHand.landmark):

                cx = int(lm.x * w)
                cy = int(lm.y * h)

                if len(self.previousLmList) == 21:
                    px = self.previousLmList[id][1]
                    py = self.previousLmList[id][2]

                    cx = int(px + (cx - px) * self.smoothFactor)
                    cy = int(py + (cy - py) * self.smoothFactor)

                self.lmList.append([id, cx, cy])
            self.previousLmList = self.lmList.copy()

            if self.results.multi_handedness:
                label = self.results.multi_handedness[handNo].classification[0].label

                # Webcam đang mirror nên đảo lại
                if label == "Left":
                    self.handType = "Right"
                else:
                    self.handType = "Left"

        if len(self.lmList) == 0:
            self.lmList = oldLmList

        return self.lmList

    def fingersUp(self):

        fingers = []

        if len(self.lmList) == 0:
            return fingers

        # Thumb

        thumb_tip = self.lmList[4][1]
        thumb_joint = self.lmList[3][1]

        if self.handType == "Right":

            if thumb_tip < thumb_joint:
                fingers.append(0)
            else:
                fingers.append(1)

        else:

            if thumb_tip > thumb_joint:
                fingers.append(0)
            else:
                fingers.append(1)

        # Index Middle Ring Pinky

        for tip in [8, 12, 16, 20]:

            if self.lmList[tip][2] < self.lmList[tip - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers