import cv2
import numpy as np
import time
import HandTracking as ht
import autopy  # Install using "pip install autopy"

## Variables Declaration
pTime = 0  # Used to calculate frame rate
width = 640  # Width of Camera
height = 480  # Height of Camera
frameR = 100  # Frame Rate
smoothening = 8  # Smoothening Factor
prev_x, prev_y = 0, 0  # Previous coordinates
curr_x, curr_y = 0, 0  # Current coordinates
roi_radius = 50  # Adjust the radius based on your preference
roi_center = (width // 2, height // 2)  # Initial center of the ROI


cap = cv2.VideoCapture(0)  # Getting video feed from the webcam
cap.set(3, width)  # Adjusting size
cap.set(4, height)

detector = ht.handDetector(maxHands=1)  # Detecting one hand at max
screen_width, screen_height = autopy.screen.size()  # Getting the screen size
while True:
    success, img = cap.read()
    img = detector.findHands(img)  # Finding the hand
    lmlist, bbox = detector.findPosition(img)  # Getting position of hand

    if len(lmlist) != 0:
        x, y = lmlist[8][1:]  # Assuming the center of the palm (landmark 8) for tracking

        # Dynamically adjust ROI based on hand's position
        roi_center = (int(x), int(y))

        # Calculate ROI boundaries
        roi_x1 = max(0, roi_center[0] - roi_radius)
        roi_y1 = max(0, roi_center[1] - roi_radius)
        roi_x2 = min(width, roi_center[0] + roi_radius)
        roi_y2 = min(height, roi_center[1] + roi_radius)

        fingers = detector.fingersUp()

        # Draw the dynamic ROI
        cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 255), 2)
        if fingers[1] == 1 and fingers[2] == 0:  # If fore finger is up and middle finger is down
            x3 = np.interp(roi_x1, (frameR, width - frameR), (0, screen_width))
            y3 = np.interp(roi_y1, (frameR, height - frameR), (0, screen_height))

            curr_x = prev_x + (x3 - prev_x) / smoothening
            curr_y = prev_y + (y3 - prev_y) / smoothening

            autopy.mouse.move(screen_width - curr_x, curr_y)  # Moving the cursor
            cv2.circle(img, (roi_x1, roi_y1), 7, (255, 0, 255), cv2.FILLED)
            prev_x, prev_y = curr_x, curr_y

        if fingers[1] == 1 and fingers[2] == 1:  # If fore finger & middle finger both are up
            length, img, lineInfo = detector.findDistance(8, 12, img)

            if length < 40:  # If both fingers are really close to each other
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()  # Perform Click

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
