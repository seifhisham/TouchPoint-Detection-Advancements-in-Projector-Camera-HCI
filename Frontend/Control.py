import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QRadioButton, QHBoxLayout, QApplication, \
    QToolButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QImage
import numpy as np

# Import required classes from your modules
from Virtual_Mouse import VirtualMouse
from FaceDetection import FaceRecognitionApp
# from setting import SettingsPage
from Frontend.setting import SettingsPage



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
        style_sheet = """
        side_bar {
           background-color: transparent;
color: black;
font-size: 14px;
font-family: Arial, sans-serif;
width: 200px;

        }
        QToolButton{
        background: transparent;
        border: none;

        }
        QPushButton {
            background-color: #335a9e; 
            color: white;
            font-size: 14px; 
            font-family: Arial, sans-serif;
            padding: 8px 16px; 
            margin-bottom: 43px;
            margin-right: 100px;
            border: 2px solid #335a9e;
            border-radius: 10px; 
            width: 200px;
        }
        QPushButton:hover {
            background-color: #153e85; 
        }
        QRadioButton {
            font-size: 25px; 
            font-family: Arial, sans-serif;
            color: black;
            margin-right: 100px;
        }
        QRadioButton::indicator {
            width: 27px; 
            height: 27px;
            border-radius: 5px;
        }
        QRadioButton::indicator::unchecked{ 
            border: 1px solid; 
            border-color: rgb(132,132,132);
            border-radius: 5px;
            background-color: white; 
            width: 27px; 
            height: 27px;
        }
       QRadioButton::indicator::checked{ 
            border: 1px solid; 
            border-color: #145369;
            border-radius: 6px;
            background-color: rgb(37, 150, 190); 
            width: 20px; 
            height: 20px; 
        }
        """
        self.setWindowTitle("Home")
        self.setStyleSheet("background-color: #ffffff;")  # Changed background color

        # Create QVBoxLayouts for left and right alignments
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignLeft)
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignRight)

        self.start_button = QPushButton("Start Hand Tracking", self)
        self.face_detection_button = QPushButton("Run Face Detection", self)
        self.stop_button = QPushButton("Stop", self)

        self.laptop_camera_radio = QRadioButton("Laptop Camera", self)
        self.mobile_camera_radio = QRadioButton("Mobile Camera", self)
        button_size = 100
        # New buttons aligned to the left
        self.button1 = QToolButton(self)
        self.button2 = QToolButton(self)
        self.button3 = QToolButton(self)
        self.button4 = QToolButton(self)

        self.button1.setIcon(QIcon("../Images/Profile.jpeg"))
        self.button2.setIcon(QIcon("../Images/Help.jpeg"))
        self.button3.setIcon(QIcon("../Images/Setting.jpeg"))
        self.button4.setIcon(QIcon("../Images/Exit.jpeg"))

        self.button1.setFixedSize(button_size, button_size)
        self.button2.setFixedSize(button_size, button_size)
        self.button3.setFixedSize(button_size, button_size)
        self.button4.setFixedSize(button_size, button_size)
        self.button1.setStyleSheet(style_sheet)
        self.button2.setStyleSheet(style_sheet)
        self.button3.setStyleSheet(style_sheet)
        self.button4.setStyleSheet(style_sheet)
        self.start_button.setStyleSheet(style_sheet)
        self.face_detection_button.setStyleSheet(style_sheet)
        self.stop_button.setStyleSheet(style_sheet)
        self.laptop_camera_radio.setStyleSheet(style_sheet)
        self.mobile_camera_radio.setStyleSheet(style_sheet)

        # self.button1.clicked.connect(self.on_icon_button1_clicked)
        # self.button2.clicked.connect(self.on_icon_button2_clicked)
        self.button3.clicked.connect(self.setting)
        self.button4.clicked.connect(self.logout)
        self.start_button.clicked.connect(self.start_hand_tracking)
        self.laptop_camera_radio.clicked.connect(self.set_laptop_camera_mode)
        self.mobile_camera_radio.clicked.connect(self.set_mobile_camera_mode)
        self.stop_button.clicked.connect(self.stop_hand_tracking)

        # Add buttons to the left layout
        left_layout.addWidget(self.button1)
        left_layout.addWidget(self.button2)
        left_layout.addWidget(self.button3)
        left_layout.addWidget(self.button4)

        # Add the rest of the widgets to the right layout
        right_layout.addWidget(self.start_button)
        right_layout.addWidget(self.face_detection_button)
        right_layout.addWidget(self.stop_button)
        right_layout.addWidget(self.laptop_camera_radio)
        right_layout.addWidget(self.mobile_camera_radio)

        # Add left and right layouts to a QHBoxLayout
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        # Add a QLabel for displaying the image
        pixmap = QPixmap("../Images/Login.jpeg")
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        main_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Set the layout for the widget
        self.setLayout(main_layout)

        self.virtual_mouse = VirtualMouse(self)
        self.is_tracking = False
        self.tracking_thread = None
        self.face_thread = None  # Initialize face thread to None
        self.face_app = FaceRecognitionApp()

        with open("./Frontend/Styles.qss", "r") as stylesheet_file:
            self.setStyleSheet(stylesheet_file.read())

    def logout(self):
        self.hide()

    def setting(self):
        self.hide()
        setting_app = SettingsPage()
        setting_app.show()

    def set_laptop_camera_mode(self):
        self.virtual_mouse.set_camera_mode("laptop")

    def set_mobile_camera_mode(self):
        self.virtual_mouse.set_camera_mode("mobile")

    def start_hand_tracking(self):
        if not self.is_tracking:
            try:
                self.is_tracking = True
                self.tracking_thread = TrackingThread(self.virtual_mouse)
                self.tracking_thread.frame_processed.connect(self.update_frame)
                self.tracking_thread.start()
            except Exception as e:
                print(f"An error occurred during hand tracking: {e}")

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)

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