import cv2
import numpy as np
import time
import HandTracking as ht
import autopy

class VirtualMouse:
    def __init__(self, app):
        self.app = app
        self.camera_mode = "laptop"  # Default camera mode
        self.cap = None
        self.set_camera()
        # self.cap.set(3, 640)
        # self.cap.set(4, 480)

        self.detector = ht.handDetector(maxHands=1)
        self.prev_fingers_touching = False  # Flag to track finger touching status

    def set_camera_mode(self, mode):
        self.camera_mode = mode
        self.set_camera()

    def set_camera(self):
        if self.camera_mode == "laptop":
            self.cap = cv2.VideoCapture(0)
        elif self.camera_mode == "mobile":
            self.cap = cv2.VideoCapture(1)

        if self.cap is not None and not self.cap.isOpened():
            print("Error: Could not open mobile camera.")
            self.camera_mode = "laptop"
            self.cap = cv2.VideoCapture(0)

    def set_smoothening(self, value):
        self.smoothening = value

    def hand_tracking_loop(self):
        pTime = 0
        width, height = 640, 480
        frameR = 100
        smoothening = 8 # Default smoothening factor
        prev_x, prev_y = 0, 0
        curr_x, curr_y = 0, 0
        roi_radius = 50
        roi_center = (width // 2, height // 2)

        screen_width, screen_height = autopy.screen.size()

        while self.app.is_tracking:
            success, img = self.cap.read()
            img = self.detector.findHands(img)
            lmlist, bbox = self.detector.findPosition(img)

            if len(lmlist) != 0:
                x, y = lmlist[8][1:]
                roi_center = (int(x), int(y))

                roi_x1 = max(0, roi_center[0] - roi_radius)
                roi_y1 = max(0, roi_center[1] - roi_radius)
                roi_x2 = min(width, roi_center[0] + roi_radius)
                roi_y2 = min(height, roi_center[1] + roi_radius)

                fingers = self.detector.fingersUp()

                cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 255), 2)

                if fingers[1] == 1 and fingers[2] == 0:
                    x3 = np.interp(roi_x1, (frameR, width - frameR), (0, screen_width))
                    y3 = np.interp(roi_y1, (frameR, height - frameR), (0, screen_height))

                    curr_x = prev_x + (x3 - prev_x) / smoothening
                    curr_y = prev_y + (y3 - prev_y) / smoothening

                    autopy.mouse.move(screen_width - curr_x, curr_y)
                    cv2.circle(img, (roi_x1, roi_y1), 7, (255, 0, 255), cv2.FILLED)
                    prev_x, prev_y = curr_x, curr_y

                if fingers[1] == 1 and fingers[2] == 1:
                    length, img, lineInfo = self.detector.findDistance(8, 12, img)

                    if length < 45 and not self.prev_fingers_touching:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        autopy.mouse.click()
                        self.prev_fingers_touching = True
                    elif length >= 45:
                        self.prev_fingers_touching = False  # Reset the flag when fingers are not touching

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            cv2.imshow("Image", img)
            cv2.waitKey(1)
