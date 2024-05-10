from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDialog, QPushButton
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

class AboutPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)  # Set layout margins

        title_label = QLabel("About Our Team Project")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        description_text = """
        The main idea of this project is to study the contactless control over a PC connected to
        any projector using only hand gestures. Moreover, reducing the cost associated with smart
        boards and many other solutions like touch projectors, which are still expensive compared
        to our software that enables anyone with his smartphone’s camera, a projector, and a simple
        setup to have an interactive surface anywhere controlled remotely with just hand gestures,
        in addition to face recognition feature - which uses YOLO algorithm - that enables gesture
        customization makes it the best affordable solution in the market that can be used for teaching
        and presentations.
        """
        description_label = QLabel(description_text)
        description_label.setFont(QFont("Arial", 14))
        description_label.setStyleSheet("""
            QLabel {
                color: #333333;
                padding: 10px;
                border: 1px solid #dddddd;
                border-radius: 8px;
            }
            """)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        version_label = QLabel("Version: 1.0")
        version_label.setFont(QFont("Arial", 12))
        layout.addWidget(version_label, alignment=Qt.AlignRight)

        author_label = QLabel(
            "Team Members:\n"
            "1. Seif Hisham - seif2010451@miuegypt.edu.eg\n"
            "2. Kirolos Emad - kirolos2015099@miuegypt.edu.eg\n"
            "3. Ahmed Zekry - ahmed2004034@miuegypt.eu.eg\n"
            "4. Marina Maurice - marina2007434@miuegypt.edu.eg"
        )
        author_label.setFont(QFont("Arial", 12))
        layout.addWidget(author_label)

        # Add logo image
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("../Images/Gestify.png")  # Replace 'Gestify.png' with your logo file path
            if logo_pixmap.isNull():
                raise FileNotFoundError("Image file not found or invalid format.")
            logo_label.setPixmap(logo_pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        except Exception as e:
            print(f"Error loading image: {e}")
        layout.addWidget(logo_label, alignment=Qt.AlignRight | Qt.AlignBottom)

        #A button to go back to the control page
        back_button = QPushButton("Back to Control Page")
        back_button.setFont(QFont("Arial", 12))
        back_button.setStyleSheet("""           
        QRadioButton::indicator::checked{ 
                border: 1px solid; 
                border-color: #145369;
                border-radius: 6px;
                background-color: rgb(37, 150, 190); 
                width: 20px; 
                height: 20px; 
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
            }""")
        back_button.clicked.connect(self.handleControlPage)
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.setWindowTitle("About Our Team Project")
        self.setGeometry(600, 100, 960, 1020)  # Set window size

    def handleControlPage(self):
        try:
            self.accept()  # Close the dialog and return control to the parent window
        except Exception as e:
            print(f"Error occurred during button click: {e}")