import math
import numpy as np

#Distance
def getDistance(lmList, p1, p2):

    x1, y1 = lmList[p1][1], lmList[p1][2]
    x2, y2 = lmList[p2][1], lmList[p2][2]

    distance = math.hypot(x2 - x1, y2 - y1)

    return distance

#HandScale
def getHandScale(lmList):

    return getDistance(lmList, 5, 17)

#Adaptive Distance
def adaptiveRange(handScale,
                  minRatio=0.30,
                  maxRatio=1.40):

    minDistance = handScale * minRatio
    maxDistance = handScale * maxRatio

    return minDistance, maxDistance

#Pinch
def isPinching(lmList,
               threshold=35):

    distance = getDistance(lmList, 4, 8)

    return distance < threshold

#Normalize
def normalize(value,
              minValue,
              maxValue):

    return np.clip(
        (value - minValue) /
        (maxValue - minValue),
        0,
        1
    )


#Smooth
def smooth(current,
           target,
           alpha=0.2):

    return current + (target - current) * alpha

#Deadzone
def deadZone(current,
             previous,
             threshold):

    if abs(current - previous) < threshold:
        return previous

    return current





