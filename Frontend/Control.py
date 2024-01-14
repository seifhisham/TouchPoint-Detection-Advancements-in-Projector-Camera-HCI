from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
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
        # Add a slider for adjusting smoothening
        self.smoothening_slider = QSlider(Qt.Horizontal)
        self.smoothening_slider.setRange(1, 20)  # Adjust the range as needed
        self.smoothening_slider.setValue(8)  # Set the initial value
        self.smoothening_slider.valueChanged.connect(self.update_smoothening)

        layout = QVBoxLayout(self)
        layout.addWidget(self.start_button)
        layout.addWidget(self.face_detection_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("Smoothening Factor"))
        layout.addWidget(self.smoothening_slider)

        self.virtual_mouse = VirtualMouse(self)
        self.smoothening_slider.valueChanged.connect(self.update_smoothening)

        self.is_tracking = False
        self.tracking_thread = None
        self.face_app = FaceRecognitionApp()

    def start_hand_tracking(self):
        if not self.is_tracking:
            self.is_tracking = True
            self.tracking_thread = TrackingThread(self.virtual_mouse)
            self.tracking_thread.frame_processed.connect(self.update_frame)
            self.tracking_thread.start()

    def stop_hand_tracking(self):
        if self.current_thread:
            self.is_tracking = False
            self.current_thread.quit()
            self.current_thread.wait()
            self.close()

    def run_face_detection(self):
        try:
            # Run the face detection and comparison code
            self.is_tracking = False  # Pause hand tracking while face detection is running
            if self.tracking_thread:
                self.tracking_thread.quit()
                self.tracking_thread.wait()

            # Run face detection and comparison
            self.face_thread = FaceRecognitionThread(self.face_app)
            self.face_thread.frame_processed.connect(self.update_frame)
            self.face_thread.finished.connect(self.run_face_detection)
            self.face_thread.start()
        except Exception as e:
            print(f"An error occurred in run_face_detection: {e}")

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)

    def update_smoothening(self, value):
        self.virtual_mouse.set_smoothening(value)