from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
from Frontend.Control import HandTrackingApp


class LoginApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Page")
        self.setGeometry(100, 100, 400, 200)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        layout = QGridLayout(self)
        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(self.login_button, 2, 0, 1, 2)  # Span two columns
        layout.addWidget(self.exit_button, 3, 0, 1, 2)   # Span two columns

        # Add some spacing between widgets
        layout.setSpacing(10)

        with open("./Frontend/Styles.qss", "r") as stylesheet_file:
            self.setStyleSheet(stylesheet_file.read())

    def login(self):
        # Add your authentication logic here
        username = self.username_input.text()
        password = self.password_input.text()

        # Example: Check if the username and password are not empty
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
        else:
            self.hide()
            tracking_app = HandTrackingApp()
            tracking_app.show()