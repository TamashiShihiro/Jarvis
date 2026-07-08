import cv2
import numpy as np
import time
from ctypes import cast, POINTER

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm


# =======================
# Audio
# =======================

devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

currentVol = minVol
lastSentVol = minVol
SMOOTH = 0.4
filteredLength = None


# =======================
# Camera
# =======================

cap = cv2.VideoCapture(0)

cap.set(3, 1280)
cap.set(4, 720)

detector = htm.HandDetector(detectionCon=0.7)

pTime = 0

# ===== Volume Lock =====
volumeLocked = False
lastPinkyState = 1


# =======================
# Loop
# =======================

while True:

    success, img = cap.read()

    if not success:
        break

    img = detector.findHands(img)

    lmList = detector.findPosition(img)



    if len(lmList) != 0:

        fingers = detector.fingersUp()

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

        length = np.hypot(x2 - x1, y2 - y1)

        if filteredLength is None:
            filteredLength = length
        else:
            filteredLength += (length - filteredLength) * 0.15

        length = filteredLength

        hx1, hy1 = lmList[5][1], lmList[5][2]
        hx2, hy2 = lmList[17][1], lmList[17][2]

        handWidth = np.hypot(hx2 - hx1, hy2 - hy1)

        minDistance = handWidth * 0.30
        maxDistance = handWidth * 1.40

        vol = np.interp(
            length,
            [minDistance, maxDistance],
            [minVol, maxVol]
        )


        vol = max(minVol, min(maxVol, vol))

        currentVol += (vol - currentVol) * SMOOTH

        # Nếu đã rất gần target thì snap luôn
        if abs(currentVol - vol) < 0.5:
            currentVol = vol

        displayPercent = np.interp(
            currentVol,
            [minVol, maxVol],
            [0, 100]
        )

        displayBar = np.interp(
            currentVol,
            [minVol, maxVol],
            [400, 150]
        )



        if not volumeLocked:
            if abs(currentVol - lastSentVol) > 0.05:
                volume.SetMasterVolumeLevel(currentVol, None)
                lastSentVol = currentVol

        # Nếu chụm hẳn tay thì báo màu xanh

        if length < 50:
            cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)

        # Thanh volume

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)

        cv2.rectangle(
            img,
            (50, int(displayBar)),
            (85, 400),
            (255, 0, 0),
            cv2.FILLED
        )

        cv2.putText(
            img,
            f"{int(displayPercent)} %",
            (35, 430),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2
        )

        if len(fingers) == 5:

            pinky = fingers[4]

            # Chỉ toggle khi chuyển từ UP -> DOWN
            if lastPinkyState == 1 and pinky == 0:
                volumeLocked = not volumeLocked
                print("TOGGLE")

            lastPinkyState = pinky


    # FPS

    cTime = time.time()

    fps = 1 / (cTime - pTime)

    pTime = cTime

    cv2.putText(
        img,
        f"FPS: {int(fps)}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Hand Volume", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()