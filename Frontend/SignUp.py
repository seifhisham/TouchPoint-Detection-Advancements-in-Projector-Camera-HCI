import os

import cv2
import face_recognition
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QDialog, QFileDialog, QFormLayout
)

from Database import DatabaseHandler
from Frontend.Control import HandTrackingApp


class SignupApp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Button style sheet
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
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #153e85; 
        }
        QLineEdit {
            border: 1px solid #5a606b; 
            border-radius: 10px;
            padding: 5px; 
            font-weight: bold;
        }
        """

        self.db_handler = DatabaseHandler(database_path='../TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/gestify.db')

        font = QFont()
        font.setPointSize(18)
        font2 = QFont()
        font2.setPointSize(25)
        font3 = QFont()
        font3.setPointSize(10)
        font3.setBold(True)

        main_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        self.showMaximized()
        self.setWindowTitle("Sign up")
        self.setModal(True)  # Make the dialog modal (blocks input to parent)
        self.setStyleSheet("background-color: #F5F5F5; color: #333;")

        # Create widgets
        self.wlabel = QLabel("Join us!")
        self.dlable = QLabel("Enter your credentials to create your account")
        self.username_label = QLabel("Username")
        self.username_label.setMaximumWidth(200)
        self.username_input = QLineEdit()
        self.username_input.setFixedWidth(300)
        self.password_label = QLabel("Password")
        self.password_label.setMaximumWidth(200)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)
        self.cpassword_label = QLabel("Confirm Password")
        self.cpassword_label.setMaximumWidth(200)
        self.cpassword_input = QLineEdit()
        self.cpassword_input.setEchoMode(QLineEdit.Password)
        self.cpassword_input.setFixedWidth(300)
        self.create_button = QPushButton("Sign Up")
        self.create_button.setFixedWidth(300)
        self.upload_button = QPushButton("Upload Face Image")
        self.upload_button.setFixedWidth(300)
        self.cancel_button = QPushButton("Login")
        self.cancel_button.setFixedWidth(300)

        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.cpassword_label, self.cpassword_input)

        # Styling
        self.create_button.setStyleSheet(button_style_sheet)
        self.upload_button.setStyleSheet(button_style_sheet)
        self.cancel_button.setStyleSheet(button_style_sheet)
        self.wlabel.setFont(font2)
        self.dlable.setFont(font)
        self.username_label.setFont(font3)
        self.password_label.setFont(font3)
        self.cpassword_label.setFont(font3)
        self.username_input.setPlaceholderText(self.username_label.text())
        self.password_input.setPlaceholderText(self.password_label.text())
        self.cpassword_input.setPlaceholderText(self.cpassword_label.text())
        self.username_input.setStyleSheet(button_style_sheet)
        self.password_input.setStyleSheet(button_style_sheet)
        self.cpassword_input.setStyleSheet(button_style_sheet)

        current_dir = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(current_dir, "../Images", "Gestify.png")

        # Add widgets to right layout
        right_layout.addWidget(self.wlabel, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.dlable, alignment=Qt.AlignLeft)
        right_layout.addLayout(form_layout)
        right_layout.addWidget(self.upload_button, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.create_button, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.cancel_button, alignment=Qt.AlignLeft)

        # Add widgets to left layout (image)
        pixmap = QPixmap(image_path)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio))
        left_layout.addWidget(image_label, alignment=Qt.AlignLeft)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addStretch(0)  # Add stretchable space between layouts
        main_layout.addLayout(right_layout)
        main_layout.addStretch(0)
        main_layout.addStretch(0)
        self.setLayout(main_layout)

        # Connect button signals to slots
        self.create_button.clicked.connect(self.create_account)
        self.upload_button.clicked.connect(self.upload_face_image)
        self.cancel_button.clicked.connect(self.cancel_signup)

        # Apply styles to buttons
        self.create_button.setFont(font)
        self.cancel_button.setFont(font)

    def create_account(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.cpassword_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Sign up Failed", "Please enter all required fields.")
        elif password != confirm_password:
            QMessageBox.warning(self, "Sign up Failed", "Passwords do not match. Please try again.")
        else:
            try:
                # Check if the user already exists
                if self.db_handler.user_exists(username):
                    QMessageBox.warning(self, "Sign up Failed",
                                        "Username already exists. Please choose a different username.")
                else:
                    # Add the user to the database
                    self.db_handler.add_user(username, password)
                    QMessageBox.information(self, "Account Created", "Account created successfully!")
                    tracking_app = HandTrackingApp(username)
                    tracking_app.show()
                    self.hide()
            except Exception as e:
                QMessageBox.warning(self, "Sign up Failed", f"Error occurred: {e}")

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

                    # Get the path to save the face image
                    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../uploaded_faces")
                    os.makedirs(save_dir, exist_ok=True)  # Create the directory if it doesn't exist

                    # Generate a unique filename for the saved face image
                    username = self.username_input.text()
                    file_basename = f"{username}.jpg"
                    save_path = os.path.join(save_dir, file_basename)

                    # Save the processed face image to disk
                    cv2.imwrite(save_path, face_img)

                    QMessageBox.information(self, "Upload Successful",
                                            f"Face image '{file_name}' saved successfully: {save_path}")
                else:
                    QMessageBox.warning(self, "Upload Failed", "No face detected in the uploaded image.")
            except Exception as e:
                QMessageBox.warning(self, "Upload Failed", f"Error processing the uploaded image: {e}")

    def cancel_signup(self):
        self.accept()