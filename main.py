import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from Frontend.Login import LoginApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = "C:/Users/aseif/PycharmProjects/TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/Images/Home.png" # Change this to the path of your icon file
    app_icon = QIcon(icon_path)

    # Set the application icon
    app.setWindowIcon(app_icon)

    login_app = LoginApp()
    login_app.show()
    sys.exit(app.exec_())
