import cv2
import time
import numpy as np
import pyautogui

import HandTrackingModule as htm
import GestureUtils as gu


# =======================
# Mouse
# =======================

screenWidth, screenHeight = pyautogui.size()

pyautogui.FAILSAFE = False


# =======================
# Camera
# =======================

cap = cv2.VideoCapture(0)

cap.set(3, 1920)
cap.set(4, 1080)

detector = htm.HandDetector(
    mode=False,
    maxHands=1,
    detectionCon=0.55,
    trackCon=0.9
)


# =======================
# Settings
# =======================

FRAME_REDUCTION = 100

SMOOTHING = 0.20

mouseX = 0
mouseY = 0

currentX = 0
currentY = 0

pTime = 0


# =======================
# Loop
# =======================

while True:

    success, img = cap.read()

    img = cv2.flip(img, 1)

    if not success:
        break

    img = detector.findHands(img)

    lmList = detector.findPosition(img)

    if len(lmList) != 0:

        fingers = detector.fingersUp()

        # Chỉ khi giơ ngón trỏ
        if fingers == [0,1,0,0,0]:

            x = lmList[8][1]
            y = lmList[8][2]

            # Hiển thị đầu ngón trỏ
            cv2.circle(
                img,
                (x, y),
                12,
                (255,0,255),
                cv2.FILLED
            )

            # Mapping Camera -> Screen
            targetX = np.interp(
                x,
                (FRAME_REDUCTION, 1920 - FRAME_REDUCTION),
                (0, screenWidth)
            )

            targetY = np.interp(
                y,
                (FRAME_REDUCTION, 1080 - FRAME_REDUCTION),
                (0, screenHeight)
            )

            # Smooth
            currentX = gu.smooth(
                currentX,
                targetX,
                SMOOTHING
            )

            currentY = gu.smooth(
                currentY,
                targetY,
                SMOOTHING
            )

            pyautogui.moveTo(
                currentX,
                currentY
            )

    # ===== Camera Frame =====

    cv2.rectangle(
        img,
        (FRAME_REDUCTION, FRAME_REDUCTION),
        (1920-FRAME_REDUCTION,1080-FRAME_REDUCTION),
        (255,255,255),
        2
    )

    # ===== FPS =====

    cTime = time.time()

    fps = 1/(cTime-pTime)

    pTime = cTime

    cv2.putText(
        img,
        f"FPS : {int(fps)}",
        (20,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Mouse Control", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()