import cv2
import time
import numpy as np
import pyautogui
import ctypes

from GestureRecognizer import GestureRecognizer
import HandTrackingModule as htm
import GestureUtils as gu


# =======================
# Mouse
# =======================

screenWidth, screenHeight = pyautogui.size()
def moveMouse(x, y):
    ctypes.windll.user32.SetCursorPos(
        int(x),
        int(y)
    )

pyautogui.FAILSAFE = False

pyautogui.PAUSE = 0


# =======================
# Camera
# =======================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

cameraWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

cameraHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

detector = htm.HandDetector(
    mode=False,
    maxHands=1,
    detectionCon=0.55,
    trackCon=0.9
)

gesture = GestureRecognizer(detector)

# =======================
# Settings
# =======================

FRAME_REDUCTION = 100

SMOOTHING = 0.20

mouseX = 0
mouseY = 0

currentX = 0
currentY = 0

lastMouseX = 0
lastMouseY = 0

MOUSE_DEADZONE = 2

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

    gesture.update()

    state = gesture.getState()



    if state is None:
        continue

    print(state["rotation"])

    pointer = state["pointer"]

    cv2.circle(
        img,
        (pointer["x"], pointer["y"]),
        8,
        (0, 255, 255),
        cv2.FILLED
    )




    if gesture.isTracking():

        # Chỉ khi giơ ngón trỏ
        if state["fingers"]["index"]:

            pointer = state["pointer"]

            x = pointer["x"]
            y = pointer["y"]

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
                (FRAME_REDUCTION,
                 cameraWidth - FRAME_REDUCTION),
                (0, screenWidth)
            )

            targetY = np.interp(
                y,
                (FRAME_REDUCTION,
                 cameraHeight - FRAME_REDUCTION),
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

            if (
                    abs(currentX - lastMouseX) > MOUSE_DEADZONE or
                    abs(currentY - lastMouseY) > MOUSE_DEADZONE
            ):
                moveMouse(
                    currentX,
                    currentY
                )

                lastMouseX = currentX
                lastMouseY = currentY



    # ===== Camera Frame =====

    cv2.rectangle(
        img,
        (FRAME_REDUCTION, FRAME_REDUCTION),
        (
            int(cameraWidth - FRAME_REDUCTION),
            int(cameraHeight - FRAME_REDUCTION)
        ),
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