from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QGridLayout, QMessageBox
)
from Frontend.Control import HandTrackingApp


class LoginApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Page")
        self.setGeometry(100, 100, 600, 300)  # Increased size
        self.setStyleSheet("background-color: #F5F5F5; color: #333;")  # Changed background color

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet("background-color: #3498db; color: white;")

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setStyleSheet("background-color: #e74c3c; color: white;")

        layout = QGridLayout(self)
        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(self.login_button, 2, 0, 1, 2)
        layout.addWidget(self.exit_button, 3, 0, 1, 2)

        layout.setSpacing(10)

        with open("./Frontend/Styles.qss", "r") as stylesheet_file:
            self.setStyleSheet(stylesheet_file.read())

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
        else:
            self.hide()
            tracking_app = HandTrackingApp()
            tracking_app.show()


if __name__ == "__main__":
    app = QApplication([])
    login_app = LoginApp()
    login_app.show()
    app.exec_()