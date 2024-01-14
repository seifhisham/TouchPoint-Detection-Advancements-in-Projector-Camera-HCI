from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSlider,
    QFrame  # Added for styling
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
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
        self.setGeometry(100, 100, 1000, 700)  # Increased size
        self.setStyleSheet("background-color: #F5F5F5;")  # Changed background color

        self.start_button = QPushButton("Start Hand Tracking", self)
        self.face_detection_button = QPushButton("Run Face Detection", self)
        self.stop_button = QPushButton("Stop", self)

        self.start_button.setStyleSheet("background-color: #3498db; color: white;")
        self.face_detection_button.setStyleSheet("background-color: #2ecc71; color: white;")
        self.stop_button.setStyleSheet("background-color: #e74c3c; color: white;")

        self.start_button.clicked.connect(self.start_hand_tracking)
        self.face_detection_button.clicked.connect(self.run_face_detection)
        self.stop_button.clicked.connect(self.stop_hand_tracking)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)  # Center align the image

        self.smoothening_slider = QSlider(Qt.Horizontal)
        self.smoothening_slider.setRange(1, 20)
        self.smoothening_slider.setValue(8)
        self.smoothening_slider.setStyleSheet("QSlider::handle:horizontal { background-color: #3498db; }")

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
        if self.tracking_thread:
            self.is_tracking = False
            self.tracking_thread.quit()
            self.tracking_thread.wait()
            self.close()

    def run_face_detection(self):
        try:
            self.is_tracking = False
            if self.tracking_thread:
                self.tracking_thread.quit()
                self.tracking_thread.wait()

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


