import cv2

class CameraInput:
    def __init__(self, camera_mode="laptop"):
        self.camera_mode = camera_mode
        self.cap = self.set_camera()

    def set_camera_mode(self, mode):
        self.camera_mode = mode
        self.cap = self.set_camera()

    def set_camera(self):
        if self.camera_mode == "laptop":
            cap = cv2.VideoCapture(0)
        elif self.camera_mode == "mobile":
            cap = cv2.VideoCapture(1)
        else:
            raise ValueError("Invalid camera mode")

        if cap is not None and not cap.isOpened():
            print("Error: Could not open the camera.")
            self.camera_mode = "laptop"
            cap = cv2.VideoCapture(0)

        return cap

    def read_frame(self):
        ret, frame = self.cap.read()
        return ret, frame

    def release_camera(self):
        if self.cap is not None:
            self.cap.release()