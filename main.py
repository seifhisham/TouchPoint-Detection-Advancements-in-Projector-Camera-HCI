import sys
from PyQt5.QtWidgets import QApplication
from Frontend.Login import LoginApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_app = LoginApp()
    login_app.show()
    sys.exit(app.exec_())
