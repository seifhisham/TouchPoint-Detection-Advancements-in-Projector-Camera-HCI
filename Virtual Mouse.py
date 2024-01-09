import cv2
import numpy as np
import time
import HandTracking as ht
import autopy
import tkinter as tk
from threading import Thread


class HandTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Tracking App")

        self.start_button = tk.Button(root, text="Start", command=self.start_hand_tracking)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_hand_tracking)
        self.stop_button.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.detector = ht.handDetector(maxHands=1)

        self.is_tracking = False

    def start_hand_tracking(self):
        if not self.is_tracking:
            self.is_tracking = True
            Thread(target=self.hand_tracking_loop).start()

    def stop_hand_tracking(self):
        self.is_tracking = False
        self.root.destroy()

    def hand_tracking_loop(self):
        pTime = 0 # Used to calculate frame rate
        width, height = 640, 480 # Width and height of Camera
        frameR = 100 # Frame Rate
        smoothening = 8 # Smoothening Factor
        prev_x, prev_y = 0, 0 # Previous coordinates
        curr_x, curr_y = 0, 0 # Current coordinates
        roi_radius = 50 # Adjust the radius based on your preference
        roi_center = (width // 2, height // 2) # Initial center of the ROI

        screen_width, screen_height = autopy.screen.size()

        while self.is_tracking:
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

                    if length < 40:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        autopy.mouse.click()

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            cv2.imshow("Image", img)
            cv2.waitKey(1)


if __name__ == "__main__":
    root = tk.Tk()
    app = HandTrackingApp(root)
    root.mainloop()
