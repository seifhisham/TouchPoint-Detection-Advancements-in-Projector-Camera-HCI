import os
import sys
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGroupBox, QRadioButton, QComboBox, \
    QHBoxLayout, QToolButton, QLabel, QDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from Commands import gesture_mapping
from Database import DatabaseHandler
from FaceDetection import FaceRecognitionApp

class SettingsPage(QDialog):
    def __init__(self, virtual_mouse, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setting")
        self.setStyleSheet("background-color: #ffffff;")  # Changed background color
        style_sheet = """
            QToolButton {
                background: transparent;
                border: none;
            }

            QPushButton {
                background-color: rgb(63, 122, 217); 
                color: white;
                font-size: 14px; 
                font-family: Arial, sans-serif;
                font-weight: bold; 
                padding: 8px 16px; 
                margin-bottom: 43px;
                margin-right: 100px;
                border: 2px solid rgb(63, 122, 217);
                border-radius: 10px; 
                width: 80px;
            }

            QComboBox {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                selection-background-color: rgb(63, 122, 217);
                color: white;
                background-color: rgb(63, 122, 217); 
                border-style: solid;
                border: 1px solid #3f7ad9;
                border-radius: 8px; 
                padding: 1px 0px 1px 20px;
                width: 80px;
                font-weight: bold; 
            }

            QComboBox:hover, QPushButton:hover {
                border: 1px solid rgb(63, 122, 217);
                color: white;
            }

            QComboBox:on {
                padding-top: 0px;
                padding-left: 0px;
                color: white;
                background-color: rgb(63, 122, 217);
                selection-background-color: rgb(63, 122, 217);
            }

            QComboBox:!on {
                color: white;
                background-color:rgb(63, 122, 217);
            }

            QComboBox QAbstractItemView {
                border: 2px solid rgb(63, 122, 217);
                color: black;
                selection-background-color:rgb(63, 122, 217);
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                color: white;
                border-left-width: 0px;
                border-left-color: rgb(63, 122, 217);
                border-left-style: solid; 
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                padding-left: 10px;
            }

            QRadioButton {
                font-size: 22px; 
                font-family: Arial, sans-serif;
                font-weight: bold; 
                color: black;
                margin-right: 100px;
            }

            QRadioButton::indicator {
                width: 27px; 
                height: 27px;
                border-radius: 5px;
            }

            QRadioButton::indicator::unchecked { 
                border: 1px solid; 
                border-color: rgb(132,132,132);
                border-radius: 5px;
                background-color: white; 
                width: 27px; 
                height: 27px;
            }

            QRadioButton::indicator::checked { 
                border: 1px solid; 
                border-color: #145369;
                border-radius: 6px;
                background-color: rgb(37, 150, 190); 
                width: 20px; 
                height: 20px; 
            }
        """
        self.virtual_mouse = virtual_mouse
        # Get the Current user logged in
        self.current_user = current_user

        # Initialize for account switching function
        self.face_app = FaceRecognitionApp()
        self.face_app.user_detected.connect(self.update_combo_boxes_with_user)

        # Get the database connection
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_filename = "gestify.db"
        self.db_path = os.path.join(current_dir, '..', db_filename)
        self.database = DatabaseHandler(database_path=self.db_path)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        main_layout = QHBoxLayout()

        # Left layout
        left_layout = QVBoxLayout()
        button_size = 100
        # New buttons aligned to the left
        self.button1 = QToolButton(self)
        self.button2 = QToolButton(self)
        self.button3 = QToolButton(self)
        self.button4 = QToolButton(self)

        self.selected_gesture1 = None
        self.selected_gesture2 = None
        self.selected_gesture3 = None

        self.button1.setIcon(QIcon("../Images/Home.png"))
        self.button2.setIcon(QIcon("../Images/Help.jpeg"))
        self.button3.setIcon(QIcon("../Images/Setting.jpeg"))
        self.button4.setIcon(QIcon("../Images/Exit.jpeg"))

        self.button1.setFixedSize(button_size, button_size)
        self.button2.setFixedSize(button_size, button_size)
        self.button3.setFixedSize(button_size, button_size)
        self.button4.setFixedSize(button_size, button_size)
        left_layout.addWidget(self.button1)
        left_layout.addWidget(self.button2)
        left_layout.addWidget(self.button3)
        left_layout.addWidget(self.button4)
        self.button1.setStyleSheet(style_sheet)
        self.button2.setStyleSheet(style_sheet)
        self.button3.setStyleSheet(style_sheet)
        self.button4.setStyleSheet(style_sheet)

        self.button1.clicked.connect(self.handleControlPage)
        self.button4.clicked.connect(self.logout)

        main_layout.addLayout(left_layout)
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignRight)
        # Add enable features group box
        self.enable_features_group = QGroupBox("Settings")
        enable_features_layout = QVBoxLayout()
        self.face_detection = QRadioButton("Face Detection")
        self.face_detection.setStyleSheet(style_sheet)
        enable_features_layout.addWidget(self.face_detection)
        self.enable_features_group.setLayout(enable_features_layout)
        #right_layout.addWidget(self.enable_features_group)

        # Add select action group box
        self.select_action_group = QGroupBox("Customize gesture")
        select_action_layout = QHBoxLayout()
        select_action_layout.setAlignment(self.select_action_group, Qt.AlignCenter)
        # Add icon and combo box
        icon_label1 = QLabel()
        pixmap1 = QPixmap("../Images/Gesture3.jpeg")
        icon_label1.setPixmap(pixmap1.scaled(50, 50))
        select_action_layout.addWidget(icon_label1)
        self.mode_combobox1 = QComboBox(self)
        self.mode_combobox1.setStyleSheet(style_sheet)
        select_action_layout.addWidget(self.mode_combobox1)
        select_action_layout.addStretch(1)

        icon_label2 = QLabel()
        pixmap2 = QPixmap("../Images/Gesture2.jpeg")
        icon_label2.setPixmap(pixmap2.scaled(50, 50))
        select_action_layout.addWidget(icon_label2)
        self.mode_combobox2 = QComboBox(self)
        self.mode_combobox2.setStyleSheet(style_sheet)
        select_action_layout.addWidget(self.mode_combobox2)
        select_action_layout.addStretch(1)

        icon_label3 = QLabel()
        pixmap3 = QPixmap("../Images/Gesture1.jpeg")
        icon_label3.setPixmap(pixmap3.scaled(50, 50))
        select_action_layout.addWidget(icon_label3)
        self.mode_combobox3 = QComboBox(self)
        self.mode_combobox3.setStyleSheet(style_sheet)
        select_action_layout.addWidget(self.mode_combobox3)
        select_action_layout.addStretch(1)

        self.populate_comboboxes()

        self.mode_combobox1.currentIndexChanged.connect(self.update_mode1)
        self.mode_combobox2.currentIndexChanged.connect(self.update_mode2)
        self.mode_combobox3.currentIndexChanged.connect(self.update_mode3)

        self.select_action_group.setLayout(select_action_layout)
        right_layout.addWidget(self.select_action_group)

        # Add switch customized actions button to the left layout
        self.switch_customized_actions_button = QPushButton("Save")
        self.switch_customized_actions_button.setStyleSheet(style_sheet)
        self.switch_customized_actions_button.clicked.connect(self.handleSaveButtonClick)
        empbox = QHBoxLayout()
        pixmap = QPixmap("../Images/Controls.jpeg")
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)
        empbox.addWidget(self.image_label, alignment=Qt.AlignCenter)
        empbox.addStretch(1)
        right_layout.addLayout(empbox)
        right_layout.addStretch(1)
        right_layout.addWidget(self.switch_customized_actions_button, alignment=Qt.AlignRight)
        right_layout.addLayout(enable_features_layout)
        right_layout.addLayout(select_action_layout)

        right_layout.addStretch(1)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def populate_comboboxes(self):
        default_text = "Select Gesture Command"
        self.mode_combobox1.addItem(default_text)
        self.mode_combobox2.addItem(default_text)
        self.mode_combobox3.addItem(default_text)

        gesture_commands = list(gesture_mapping.keys())

        self.mode_combobox1.addItems(gesture_commands)
        self.mode_combobox2.addItems(gesture_commands)
        self.mode_combobox3.addItems(gesture_commands)

    def update_mode1(self, index):
        try:
            if self.virtual_mouse is not None:
                self.selected_gesture1 = self.mode_combobox1.currentText()
                self.virtual_mouse.set_selected_gesture1(self.selected_gesture1)
                self.virtual_mouse.Combobox1_gesture()
            else:
                print("Error: virtual_mouse is not initialized.")
        except Exception as e:
            print(f"An error occurred in update_mode1: {e}")

    def update_mode2(self, index):
        self.selected_gesture2 = self.mode_combobox2.currentText()
        self.virtual_mouse.set_selected_gesture2(self.selected_gesture2)
        self.virtual_mouse.Combobox2_gesture()

    def update_mode3(self, index):
        self.selected_gesture3 = self.mode_combobox3.currentText()
        self.virtual_mouse.set_selected_gesture3(self.selected_gesture3)
        self.virtual_mouse.Combobox3_gesture()

    @pyqtSlot(str)
    def update_combo_boxes_with_user(self, username):
        try:
            print(f"Updating combo boxes for user: {username}")
            # Fetch user gestures from database based on identified username
            user_data = self.database.fetch_user_gestures(username)
            print(f"User data fetched: {user_data}")
            if user_data:
                gesture1, gesture2, gesture3 = user_data
                print(f"Setting combo boxes - Gesture1: {gesture1}, Gesture2: {gesture2}, Gesture3: {gesture3}")
                self.mode_combobox1.setCurrentText(gesture1)
                self.mode_combobox2.setCurrentText(gesture2)
                self.mode_combobox3.setCurrentText(gesture3)
        except Exception as e:
            print(f"Error updating combo boxes with user settings: {e}")

    def handleSaveButtonClick(self):
        try:
            # Get selected gesture commands from combo boxes
            gesture1 = self.mode_combobox1.currentText()
            gesture2 = self.mode_combobox2.currentText()
            gesture3 = self.mode_combobox3.currentText()

            # Create an instance of DatabaseHandler
            db_handler = DatabaseHandler(database_path=self.db_path)

            # Update the gestures for the current user in the database
            db_handler.update_gestures(self.current_user, gesture1, gesture2, gesture3)

            if not os.path.exists(self.db_path):
                print(f"Database file not found: {self.db_path}")
        except Exception as e:
            QMessageBox.warning(self, "Upload Failed", f"Error Saving The Gestures: {e}")

    def handleControlPage(self):
        try:
            self.accept()
        except Exception as e:
            print(f"Error occurred during Save button click: {e}")
    def logout(self):
        self.close()