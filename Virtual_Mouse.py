import cv2
import numpy as np
import time
import autopy

from Commands import gesture_mapping
from HandTracking import handDetector
from homography_mapping import calibrate_homography
from preprocessing import preprocess_image
from camera_input import CameraInput

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


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

        self.saved_volume = 0

        self.detector = handDetector(maxHands=1)
        self.prev_fingers_touching = False

        #self.mode = "Default"
        self.selected_gesture1 = None
        self.selected_gesture2 = None
        self.selected_gesture3 = None
        self.selected_mode = "Default"

    def set_homography_mapping(self, enabled):
        self.homography_enabled = enabled

    def calibrate_homography(self, calibration_image):
        return calibrate_homography(calibration_image, self.screen_points)

    def set_camera_mode(self, mode):
        self.camera_mode = mode
        self.camera.set_camera_mode(mode)

    def set_camera(self):
        self.camera.set_camera()
        self.calibrated = False

    def set_mode1(self, mode):
        self.mode = mode
        # Depending on the mode, you may want to update settings or perform specific actions
    def set_mode2(self, mode):
        self.mode = mode

    def set_mode3(self, mode):
        self.mode = mode

    def set_selected_gesture1(self, selected_gesture):
        self.selected_gesture1 = selected_gesture

    def set_selected_gesture2(self, selected_gesture):
        self.selected_gesture2 = selected_gesture
    def set_selected_gesture3(self, selected_gesture):
        self.selected_gesture3 = selected_gesture
    def Combobox1_gesture(self):
        print("first three fingers")
        print("selected_gesture:", self.selected_gesture1)
        if self.selected_gesture1 is not None:
            print("Executing gesture command:", self.selected_gesture1)
            if self.selected_gesture1 in gesture_mapping:
                gesture_mapping[self.selected_gesture1]()
                print("Gesture executed successfully.")
            else:
                print("Gesture not found in mapping.")
        else:
            print("No selected gesture.")

    def Combobox2_gesture(self):
        print("last three fingers")
        print("selected_gesture:", self.selected_gesture2)
        if self.selected_gesture2 is not None:
            print("Executing gesture command:", self.selected_gesture2)
            if self.selected_gesture2 in gesture_mapping:
                gesture_mapping[self.selected_gesture2]()
                print("Gesture executed successfully.")
            else:
                print("Gesture not found in mapping.")
        else:
            print("No selected gesture.")

    def Combobox3_gesture(self):
        print("five fingers")
        print("selected_gesture:", self.selected_gesture3)
        if self.selected_gesture3 is not None:
            print("Executing gesture command:", self.selected_gesture3)
            if self.selected_gesture3 in gesture_mapping:
                gesture_mapping[self.selected_gesture3]()
                print("Gesture executed successfully.")
            else:
                print("Gesture not found in mapping.")
        else:
            print("No selected gesture.")

    def control_volume(self, length, fingers):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        volRange = volume.GetVolumeRange()
        minVol = volRange[0]
        maxVol = volRange[1]

        volPer = np.interp(length, [50, 200], [0, 100])
        volPer = round(volPer)  # Round to nearest integer for percentage

        # If pinky is down, set the volume percentage
        if not fingers[4]:
            volume.SetMasterVolumeLevelScalar(volPer / 100, None)
        else:
            # If pinky is up, revert to the previous volume level
            volume.SetMasterVolumeLevelScalar(self.saved_volume / 100, None)

        # Store the current volume level if all fingers are closed
        if all(not finger for finger in fingers):
            self.saved_volume = volume.GetMasterVolumeLevelScalar() * 100

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
                length, img, lineInfo = self.detector.findDistance(4, 8, img)

                cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 255), 2)

                if fingers[0] == 1 and fingers[1] == 1:
                    try:
                        self.control_volume(length, fingers)
                    except Exception as e:
                        print(f"An error occurred while controlling volume: {e}")

                if fingers[1] == 1 and fingers[2] == 0:
                    x3 = np.interp(roi_center[0], (frameR, width - frameR), (0, screen_width))
                    y3 = np.interp(roi_center[1], (frameR, height - frameR), (0, screen_height))

                    curr_x = prev_x + (x3 - prev_x) / smoothening
                    curr_y = prev_y + (y3 - prev_y) / smoothening

                    autopy.mouse.move(screen_width - curr_x, curr_y)
                    cv2.circle(img, (roi_center[0], roi_center[1]), 7, (255, 0, 255), cv2.FILLED)
                    prev_x, prev_y = curr_x, curr_y

                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
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
                #fifth gesture
                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                    try:
                        self.Combobox1_gesture()
                    except Exception as e:
                        print(f"An error occurred in hand tracking loop: {e}")
                elif fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                    try:
                        self.Combobox2_gesture()
                    except Exception as e:
                        print(f"An error occurred in hand tracking loop: {e}")
                elif fingers[0] == 1 and fingers[4] == 1:
                    try:
                        self.Combobox3_gesture()
                    except Exception as e:
                        print(f"An error occurred in hand tracking loop: {e}")
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