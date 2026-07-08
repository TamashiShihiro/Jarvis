import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm
import HomeAssistant as ha
import math

devices = [
    {
        "name": "LIGHT",
        "entity": "switch.1_gang",

        "x": 0,
        "y": 0,
        "w": 0,
        "h": 0,

        "holdStart": None,
        "lastSeen": 0
    }
]



TARGET_HOLD_TIME = 1.5      # Giữ 1.5 giây
COOLDOWN_TIME = 2           # Cooldown 2 giây

lastTriggerTime = 0

cooldown = False

pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
detector = htm.HandDetector()


while True:
    success, img = cap.read()
    height, width = img.shape[:2]
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if len(lmList) != 0:
        fingers = detector.fingersUp()

        if len(fingers) == 5:

            thumb, index, middle, ring, pinky = fingers

            isPointing = (
                    index == 1 and
                    middle == 0 and
                    ring == 0 and
                    pinky == 0
            )

        else:
            isPointing = False


        # Gesture: Pointing
        if isPointing:
            x1 = lmList[5][1]
            y1 = lmList[5][2]

            x2 = lmList[8][1]
            y2 = lmList[8][2]

            dx = x2 - x1
            dy = y2 - y1

            distance = math.sqrt(dx * dx + dy * dy)



            if distance != 0:
                dx /= distance
                dy /= distance

            RAY_LENGTH = 1200

            endX = int(x2 + dx * RAY_LENGTH)
            endY = int(y2 + dy * RAY_LENGTH)


            currentTime = time.time()

            if currentTime - lastTriggerTime < COOLDOWN_TIME:
                cooldown = True
            else:
                cooldown = False

            for device in devices:
                device["x"] = 20
                device["y"] = 20

                device["w"] = width - 40

                device["h"] = 70

            for device in devices:

                hit = False

                for i in range(100):

                    t = i / 100

                    px = x2 + (endX - x2) * t
                    py = y2 + (endY - y2) * t

                    if device["x"] <= px <= device["x"] + device["w"] and \
                            device["y"] <= py <= device["y"] + device["h"]:
                        hit = True
                        break

                if hit:

                    targetFound = True

                    device["lastSeen"] = currentTime

                    if device["holdStart"] is None:
                        device["holdStart"] = currentTime

                    holdTime = currentTime - device["holdStart"]
                    progress = min(holdTime / TARGET_HOLD_TIME, 3.0)

                    cv2.rectangle(
                        img,
                        (device["x"], device["y"]),
                        (
                            int(device["x"] + device["w"] * progress),
                            device["y"] + device["h"]
                        ),
                        (0, 255, 0),
                        -1
                    )

                    # Vẽ lại viền để không bị mất
                    cv2.rectangle(
                        img,
                        (device["x"], device["y"]),
                        (device["x"] + device["w"], device["y"] + device["h"]),
                        (255, 255, 255),
                        2
                    )

                    cv2.putText(
                        img,
                        f"{holdTime:.1f}s",
                        (device["x"] - 20, device["y"] + 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

                    if holdTime >= TARGET_HOLD_TIME and not cooldown:
                        #print("TOGGLE")

                        ha.toggle(device["entity"])

                        lastTriggerTime = currentTime

                        device["holdStart"] = None

            if not hit:
                device["holdStart"] = None


            cv2.line(img,
                     (x2, y2),
                     (endX, endY),
                     (0, 0, 255),
                     3)

        else:

            for device in devices:

                if time.time() - device["lastSeen"] > 0.3:
                    device["holdStart"] = None

        #print(detector.handType, fingers)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img,
                str(int(fps)),
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 255, 0),
                2)

    for device in devices:
        cv2.rectangle(
            img,
            (device["x"], device["y"]),
            (
                device["x"] + device["w"],
                device["y"] + device["h"]
            ),
            (255, 255, 255),
            2
        )

        cv2.putText(
            img,
            device["name"],
            (
                device["x"] + 20,
                device["y"] + 50
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

    if cooldown:
        remain = COOLDOWN_TIME - (currentTime - lastTriggerTime)

        cv2.putText(
            img,
            f"Cooldown {remain:.1f}s",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()