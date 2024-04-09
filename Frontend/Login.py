import os

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFileDialog, QHBoxLayout
)
from Frontend.Control import HandTrackingApp
from Database import DatabaseHandler
import face_recognition

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()

        button_style_sheet = """
        QPushButton {
            background-color: #335a9e; 
            color: white;
            font-size: 14px; 
            font-family: Arial, sans-serif;
            padding: 8px 16px; 
            margin-bottom: 43px;
            border: 2px solid #335a9e;
            border-radius: 10px; 
        }
        QPushButton:hover {
            background-color: #153e85; 
        }
        QLineEdit {
            border: 1px solid #5a606b; 
            border-radius: 10px;
            padding: 5px; 
        }
        """

        font = QFont()
        font.setPointSize(18)
        font2 = QFont()
        font2.setPointSize(25)

        main_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(current_dir, "../Images", "Login.jpeg")

        self.showMaximized()
        self.setWindowTitle("Login Page")
        self.setStyleSheet("background-color: #F5F5F5; color: #333;")

        # Database Connection
        self.db_handler = DatabaseHandler(database_path='../TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/gestify.db')

        # Create widgets
        self.wlabel = QLabel("Welcome back!")
        self.dlable = QLabel("Enter your credentials to access your account")
        self.username_label = QLabel("Email Address")
        self.username_label.setMaximumWidth(200)
        self.username_input = QLineEdit()
        self.username_input.setFixedWidth(300)
        self.password_label = QLabel("Password")
        self.password_label.setMaximumWidth(200)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(300)
        self.upload_button = QPushButton("Upload Face Image")
        self.upload_button.setFixedWidth(300)

        # Styling
        self.login_button.setStyleSheet(button_style_sheet)
        self.upload_button.setStyleSheet(button_style_sheet)
        self.wlabel.setFont(font2)
        self.dlable.setFont(font)
        self.username_input.setPlaceholderText(self.username_label.text())
        self.password_input.setPlaceholderText(self.password_label.text())
        self.username_input.setStyleSheet(button_style_sheet)
        self.password_input.setStyleSheet(button_style_sheet)

        # Add widgets to right layout
        right_layout.addWidget(self.wlabel, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.dlable, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.username_label, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.username_input, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.password_label, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.password_input, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.login_button, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.upload_button, alignment=Qt.AlignLeft)

        # Add widgets to left layout
        pixmap = QPixmap(image_path)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setPixmap(pixmap.scaled(1400, 900, Qt.KeepAspectRatio))
        left_layout.addWidget(image_label, alignment=Qt.AlignLeft)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addStretch(0)  # Add stretchable space between layouts
        main_layout.addLayout(right_layout)
        main_layout.addStretch(0)
        main_layout.addStretch(0)
        self.setLayout(main_layout)

        # Connect button signals to slots
        self.login_button.clicked.connect(self.login)
        self.upload_button.clicked.connect(self.upload_face_image)

        # Apply styles to buttons
        self.login_button.setFont(font)
        self.upload_button.setFont(font)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
        else:
            # Check if the user exists in the database
            user_data = self.db_handler.check_user(username, password)

            if user_data:
                # User found, navigate to the next page (in this case, HandTrackingApp)
                self.hide()
                tracking_app = HandTrackingApp()
                tracking_app.show()
            else:
                # User not found, create a new account
                QMessageBox.warning(self, "User Not Found", "User not found. Create a new account...")
                # You can add logic here to handle account creation if needed

    def upload_face_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Face Image", "",
                                                   "Image Files (*.png *.jpg *.bmp *.jpeg);;All Files (*)",
                                                   options=options)

        if file_name:
            try:
                # Load the face image using OpenCV
                image = cv2.imread(file_name)

                # Convert BGR image to RGB (required by face_recognition)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Detect faces in the image
                face_locations = face_recognition.face_locations(image_rgb)

                if face_locations:
                    # Get the first detected face (assuming one face per image)
                    top, right, bottom, left = face_locations[0]

                    # Crop the face region from the image
                    face_img = image[top:bottom, left:right]

                    # Resize the face image (optional, adjust as needed)
                    face_img = cv2.resize(face_img, (256, 256))

                    # Get the username and password (you can modify this part as needed)
                    username = self.username_input.text()
                    password = self.password_input.text()

                    # Insert the face image into the database (convert to bytes if needed)
                    face_id = self.db_handler.insert_face_image(username, password, face_img)

                    if face_id is not None:
                        QMessageBox.information(self, "Upload Successful",
                                                f"Face image '{file_name}' (ID: {face_id}) uploaded successfully.")
                    else:
                        QMessageBox.warning(self, "Upload Failed", "Error inserting face image into the database.")
                else:
                    QMessageBox.warning(self, "Upload Failed", "No face detected in the uploaded image.")
            except Exception as e:
                QMessageBox.warning(self, "Upload Failed", f"Error processing the uploaded image: {e}")