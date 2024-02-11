import cv2
import numpy as np
import time
import autopy
from HandTracking import handDetector
from homography_mapping import calibrate_homography
from preprocessing import preprocess_image
from camera_input import CameraInput

class VirtualMouse:
    def __init__(self, app):
        self.app = app
        self.camera_mode = "laptop"
        self.camera = CameraInput(camera_mode=self.camera_mode)
        # self.cap = None
        # self.set_camera()
        self.homography_enabled = False
        self.screen_points = []
        self.calibrated = False

        self.detector = handDetector(maxHands=1)
        self.prev_fingers_touching = False

    def set_homography_mapping(self, enabled):
        self.homography_enabled = enabled

    def calibrate_homography(self, calibration_image):
        self.screen_points = []
        return calibrate_homography(calibration_image, self.screen_points)

    def set_camera_mode(self, mode):
        self.camera_mode = mode
        self.camera.set_camera_mode(mode)

    def set_camera(self):
        self.camera.set_camera()
        self.calibrated = False

    def hand_tracking_loop(self):
        pTime = 0
        width, height = 640, 480
        frameR = 100
        smoothening = 8
        prev_x, prev_y = 0, 0
        curr_x, curr_y = 0, 0
        roi_radius = 50
        roi_center = (width // 2, height // 2)
        screen_width, screen_height = autopy.screen.size()
        homography_matrix = None

        while self.app.is_tracking:
            ret, img = self.camera.read_frame()
            img = self.detector.findHands(img)
            lmlist, bbox = self.detector.findPosition(img)

            if len(lmlist) != 0:
                x, y = lmlist[8][1:]

                if self.homography_enabled and not self.calibrated:
                    calibration_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    homography_matrix = self.calibrate_homography(calibration_image)
                    self.calibrated = True

                if homography_matrix is not None and self.homography_enabled:
                    mapped_point = homography_mapping((x, y), width, height, screen_width, screen_height,
                                                      homography_matrix)
                    roi_center = (int(mapped_point[0]), int(mapped_point[1]))
                else:
                    roi_center = (int(x), int(y))

                roi_x1 = max(0, roi_center[0] - roi_radius)
                roi_y1 = max(0, roi_center[1] - roi_radius)
                roi_x2 = min(width, roi_center[0] + roi_radius)
                roi_y2 = min(height, roi_center[1] + roi_radius)

                fingers = self.detector.fingersUp()

                cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 255), 2)

                if fingers[1] == 1 and fingers[2] == 0:
                    x3 = np.interp(roi_center[0], (frameR, width - frameR), (0, screen_width))
                    y3 = np.interp(roi_center[1], (frameR, height - frameR), (0, screen_height))

                    curr_x = prev_x + (x3 - prev_x) / smoothening
                    curr_y = prev_y + (y3 - prev_y) / smoothening

                    autopy.mouse.move(screen_width - curr_x, curr_y)
                    cv2.circle(img, (roi_center[0], roi_center[1]), 7, (255, 0, 255), cv2.FILLED)
                    prev_x, prev_y = curr_x, curr_y

                elif fingers[1] == 1 and fingers[2] == 1:
                    length, img, lineInfo = self.detector.findDistance(8, 12, img)

                    if length < 40 and not self.prev_fingers_touching:
                        cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                        autopy.mouse.click()
                        self.prev_fingers_touching = True
                    elif length >= 40:
                        self.prev_fingers_touching = False

                elif fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)

                    if prev_x != 0 and prev_y != 0:
                        x3 = np.interp(roi_center[0], (frameR, width - frameR), (0, screen_width))
                        y3 = np.interp(roi_center[1], (frameR, height - frameR), (0, screen_height))

                        curr_x = prev_x + (x3 - prev_x) / smoothening
                        curr_y = prev_y + (y3 - prev_y) / smoothening

                        autopy.mouse.move(screen_width - prev_x, prev_y)
                        prev_x, prev_y = curr_x, curr_y

                    # Check if fingers start touching again and stop the drag action
                    elif fingers[1] == 1 or fingers[2] == 1 or fingers[3] == 1 or fingers[4] == 1:
                        autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                else:
                    autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)


            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            img_processed = preprocess_image(img, homography_enabled=self.homography_enabled, screen_detection=True)

            cv2.imshow("Image", img)
            cv2.waitKey(1)

def homography_mapping(point, width, height, screen_width, screen_height, homography_matrix):
    mapped_point = cv2.perspectiveTransform(np.array([point], dtype=np.float32).reshape(-1, 1, 2), homography_matrix)
    return mapped_point[0][0]