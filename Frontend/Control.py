from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QHBoxLayout, QRadioButton, QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
import cv2
import numpy as np
from Virtual_Mouse import VirtualMouse
from FaceDetection import FaceRecognitionApp

class TrackingThread(QThread):
    frame_processed = pyqtSignal(np.ndarray)

    def __init__(self, virtual_mouse):
        super().__init__()
        self.virtual_mouse = virtual_mouse

    def run(self):
        self.virtual_mouse.hand_tracking_loop()

class FaceRecognitionThread(QThread):
    frame_processed = pyqtSignal(np.ndarray)

    def __init__(self, face_app):
        super().__init__()
        self.face_app = face_app

    def run(self):
        self.face_app.run_face_recognition()

class HandTrackingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Tracking App")

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_hand_tracking)

        self.face_detection_button = QPushButton("Face Detection", self)
        self.face_detection_button.clicked.connect(self.run_face_detection)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_hand_tracking)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)  # Center align the image label

        # Add a slider for adjusting smoothening
        self.smoothening_slider = QSlider(Qt.Horizontal)
        self.smoothening_slider.setRange(1, 20)  # Adjust the range as needed
        self.smoothening_slider.setValue(8)  # Set the initial value
        self.smoothening_slider.valueChanged.connect(self.update_smoothening)

        # radio buttons for camera mode selection
        self.laptop_camera_radio = QRadioButton("Laptop Camera", self)
        self.mobile_camera_radio = QRadioButton("Mobile Camera", self)

        self.homography_checkbox = QCheckBox("Use Homography Mapping", self)
        self.homography_checkbox.setChecked(False)  # Default is disabled
        self.homography_checkbox.stateChanged.connect(self.toggle_homography_mapping)

        camera_mode_layout = QVBoxLayout()
        camera_mode_layout.addWidget(self.laptop_camera_radio)
        camera_mode_layout.addWidget(self.mobile_camera_radio)
        camera_mode_layout.addStretch(1)

        # Connect radio button signals
        self.laptop_camera_radio.clicked.connect(self.set_laptop_camera_mode)
        self.mobile_camera_radio.clicked.connect(self.set_mobile_camera_mode)

        # Create a layout for buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.face_detection_button)
        buttons_layout.addWidget(self.stop_button)

        # Create a vertical layout for the entire widget
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Camera Mode"))
        layout.addLayout(camera_mode_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.image_label, 1)  # Allow image_label to expand
        layout.addWidget(self.homography_checkbox)
        layout.addWidget(QLabel("Smoothening Factor"))
        layout.addWidget(self.smoothening_slider)

        self.virtual_mouse = VirtualMouse(self)
        self.smoothening_slider.valueChanged.connect(self.update_smoothening)

        self.is_tracking = False
        self.tracking_thread = None
        self.face_thread = None  # Initialize face thread to None
        self.face_app = FaceRecognitionApp()

        with open("./Frontend/Styles.qss", "r") as stylesheet_file:
            self.setStyleSheet(stylesheet_file.read())

    def set_laptop_camera_mode(self):
        self.virtual_mouse.set_camera_mode("laptop")

    def set_mobile_camera_mode(self):
        self.virtual_mouse.set_camera_mode("mobile")

    def toggle_homography_mapping(self):
        enabled = self.homography_checkbox.isChecked()
        self.virtual_mouse.set_homography_mapping(enabled)

    def start_hand_tracking(self):
        if not self.is_tracking:
            try:
                self.is_tracking = True
                self.tracking_thread = TrackingThread(self.virtual_mouse)
                self.tracking_thread.frame_processed.connect(self.update_frame)
                self.tracking_thread.start()
            except Exception as e:
                print(f"An error occurred during hand tracking: {e}")

    def calibrate_homography(self, calibration_image):
        self.virtual_mouse.screen_points = []  # Reset screen points
        return self.virtual_mouse.calibrate_homography(calibration_image)

    def stop_hand_tracking(self):
        if self.tracking_thread and self.tracking_thread.isRunning():
            self.is_tracking = False
            self.tracking_thread.quit()
            self.tracking_thread.wait()
        elif self.face_thread and self.face_thread.isRunning():
            self.is_tracking = False
            self.face_thread.quit()
            self.face_thread.wait()
        else:
            print("No active threads to stop.")

    def run_face_detection(self):
        try:
            if self.face_thread and self.face_thread.isRunning():
                # If face detection thread is already running, do nothing
                return

            self.face_thread = FaceRecognitionThread(self.face_app)
            self.face_thread.frame_processed.connect(self.update_frame)
            self.face_thread.finished.connect(self.run_face_detection)
            self.face_thread.start()
        except Exception as e:
            print(f"An error occurred in face detection: {e}")

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)

    def update_smoothening(self, value):
        self.virtual_mouse.set_smoothening(value)
