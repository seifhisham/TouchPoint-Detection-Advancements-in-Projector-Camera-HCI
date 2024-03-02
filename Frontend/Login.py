from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from Frontend.Control import HandTrackingApp

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
        font2= QFont()
        font2.setPointSize(25)
        main_layout = QHBoxLayout()

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()
        self.showMaximized()
        self.setWindowTitle("Login Page")
        self.setStyleSheet("background-color: #F5F5F5; color: #333;")

        # Create widgets
        self.wlabel = QLabel("Welcome back!")
        self.dlable = QLabel ("Enter your credentials to access your account")
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
        self.username_label.setFont(font)
        self.password_label.setFont(font)

        # Add widgets to left layout
        right_layout.addWidget(self.wlabel,alignment=Qt.AlignLeft)
        right_layout.addWidget(self.dlable,alignment=Qt.AlignLeft)
        right_layout.addWidget(self.username_label,alignment=Qt.AlignLeft)
        right_layout.addWidget(self.username_input,alignment=Qt.AlignLeft)
        right_layout.addWidget(self.password_label,alignment=Qt.AlignLeft)
        right_layout.addWidget(self.password_input,alignment=Qt.AlignLeft)
        right_layout.addWidget(self.login_button,alignment=Qt.AlignLeft)
        self.login_button.setStyleSheet(button_style_sheet)
        self.wlabel.setFont(font2)
        self.dlable.setFont(font)
        self.username_input.setPlaceholderText(self.username_label.text())
        self.password_input.setPlaceholderText(self.password_label.text())
        self.username_input.setStyleSheet(button_style_sheet)
        self.password_input.setStyleSheet(button_style_sheet)

        # Add widgets to right layout
        pixmap = QPixmap("../Images/Login.jpeg")
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

        # Apply styles to buttons
        self.login_button.setFont(font)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
        else:
            self.hide()
            tracking_app = HandTrackingApp()
            tracking_app.show()