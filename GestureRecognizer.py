import math


class GestureRecognizer:

    def __init__(self, detector):

        self.fingerMap = {
            "thumb": (2, 3, 4),
            "index": (5, 6, 8),
            "middle": (9, 10, 12),
            "ring": (13, 14, 16),
            "pinky": (17, 18, 20)
        }

        self.detector = detector

        self.dragging = False
        self.leftClicked = False
        self.rightClicked = False

    def isPinching(self):

        if len(self.lmList) == 0:
            return False

        return self.pinchDistance() < self.handScale() * 0.32

    def update(self):

        self.lmList = self.detector.lmList

        self.handType = self.detector.handType

    def _distance(self, p1, p2):

        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]

        return math.hypot(x2 - x1, y2 - y1)

    def _vector(self, p1, p2):

        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]

        return (
            x2 - x1,
            y2 - y1
        )

    def getPalmRotation(self):

        if len(self.lmList) == 0:
            return None

        vx, vy = self._vector(5, 17)

        angle = math.degrees(
            math.atan2(
                vy,
                vx
            )
        )

        return angle

    def _angle(self, p1, p2, p3):

        ax = self.lmList[p1][1]
        ay = self.lmList[p1][2]

        bx = self.lmList[p2][1]
        by = self.lmList[p2][2]

        cx = self.lmList[p3][1]
        cy = self.lmList[p3][2]

        ba = (ax - bx, ay - by)
        bc = (cx - bx, cy - by)

        dot = ba[0] * bc[0] + ba[1] * bc[1]

        mag1 = math.hypot(*ba)
        mag2 = math.hypot(*bc)

        if mag1 == 0 or mag2 == 0:
            return 0

        cos = dot / (mag1 * mag2)

        cos = max(-1, min(1, cos))

        return math.degrees(math.acos(cos))


    def handScale(self):

        if len(self.lmList) == 0:
            return 0

        return self._distance(5, 17)

    def pinchDistance(self):

        if len(self.lmList) == 0:
            return 0

        return self._distance(4, 8)

    def pointPosition(self):

        if len(self.lmList) == 0:
            return None

        return (
            self.lmList[8][1],
            self.lmList[8][2]
        )

    def isFingerExtended(self, finger):

        if len(self.lmList) == 0:
            return False

        if finger not in self.fingerMap:
            return False

        mcp, pip, tip = self.fingerMap[finger]

        angle = self._angle(mcp, pip, tip)

        if angle > 160:
            return True

        return False

    def isThumbExtended(self):

        if len(self.lmList) == 0:
            return False

        wrist = self.lmList[0]
        mcp = self.lmList[2]
        tip = self.lmList[4]

        dTip = math.hypot(
            tip[1] - wrist[1],
            tip[2] - wrist[2]
        )

        dMcp = math.hypot(
            mcp[1] - wrist[1],
            mcp[2] - wrist[2]
        )

        return dTip > dMcp * 1.2



    def _isAbove(self, p1, p2):

        return self.lmList[p1][2] < self.lmList[p2][2]

    def getIndexRay(self, extend=0.4):

        if len(self.lmList) == 0:
            return None

        # Gốc ngón trỏ
        x1 = self.lmList[5][1]
        y1 = self.lmList[5][2]



        # Đầu ngón trỏ
        x2 = self.lmList[8][1]
        y2 = self.lmList[8][2]

        dx = x2 - x1
        dy = y2 - y1

        length = math.hypot(dx, dy)

        if length == 0:
            return None

        dx /= length
        dy /= length

        extendLength = self.handScale() * 0.45

        endX = x2 + dx * extendLength
        endY = y2 + dy * extendLength

        return (
            int(endX),
            int(endY)
        )

    def isTracking(self):

        return len(self.lmList) != 0

    def getState(self):

        if not self.isTracking():
            return None

        ray = self.getIndexRay()

        return {

            "tracking": True,

            "pointer": {
                "x": ray[0] if ray else None,
                "y": ray[1] if ray else None
            },

            "rotation": self.getPalmRotation(),

            "pinch": {
                "distance": self.pinchDistance()
            },

            "fingers": {
                "thumb": self.isThumbExtended(),
                "index": self.isFingerExtended("index"),
                "middle": self.isFingerExtended("middle"),
                "ring": self.isFingerExtended("ring"),
                "pinky": self.isFingerExtended("pinky")
            },

            "scale": self.handScale()

        }