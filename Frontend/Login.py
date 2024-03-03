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

        self.showMaximized()
        self.setWindowTitle("Login Page")
        self.setStyleSheet("background-color: #F5F5F5; color: #333;")

        # Database Connection
        self.db_handler = DatabaseHandler(database_path='./gestify.db')

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
        pixmap = QPixmap("C:/Users/aseif/PycharmProjects/TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/Images/Login.jpeg")
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
            self.hide()
            tracking_app = HandTrackingApp()
            tracking_app.show()

    def upload_face_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Face Image", "", "Image Files (*.png *.jpg *.bmp *.jpeg);;All Files (*)", options=options)

        if file_name:
            try:
                # Handle the uploaded face image
                image = face_recognition.load_image_file(file_name)
                face_encoding = face_recognition.face_encodings(image)

                if face_encoding:
                    # Get the username and password (you can modify this part as needed)
                    username = self.username_input.text()
                    password = self.password_input.text()

                    # Insert the face encoding into the database and get the ID
                    face_id = self.db_handler.insert_face_encoding(username, password, face_encoding[0].tobytes())

                    if face_id is not None:
                        QMessageBox.information(self, "Upload Successful", f"Face image '{file_name}' (ID: {face_id}) uploaded and encoded successfully.")
                    else:
                        QMessageBox.warning(self, "Upload Failed", "Error inserting face encoding into the database.")
                else:
                    QMessageBox.warning(self, "Upload Failed", "No face detected in the uploaded image.")
            except Exception as e:
                QMessageBox.warning(self, "Upload Failed", f"Error processing the uploaded image: {e}")
