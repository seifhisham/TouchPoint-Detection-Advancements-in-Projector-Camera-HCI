from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from Virtual_Mouse import VirtualMouse

class TrackingThread(QThread):
    frame_processed = pyqtSignal(np.ndarray)

    def __init__(self, virtual_mouse):
        super().__init__()
        self.virtual_mouse = virtual_mouse

    def run(self):
        self.virtual_mouse.hand_tracking_loop()

class HandTrackingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Tracking App")

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_hand_tracking)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_hand_tracking)

        self.image_label = QLabel(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.image_label)

        self.virtual_mouse = VirtualMouse(self)

        self.is_tracking = False
        self.tracking_thread = None

    def start_hand_tracking(self):
        if not self.is_tracking:
            self.is_tracking = True
            self.tracking_thread = TrackingThread(self.virtual_mouse)
            self.tracking_thread.frame_processed.connect(self.update_frame)
            self.tracking_thread.start()

    def stop_hand_tracking(self):
        self.is_tracking = False
        self.tracking_thread.quit()
        self.tracking_thread.wait()
        self.close()

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)
