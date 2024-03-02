import cv2
import numpy as np
import torch
import face_recognition
import preprocessing
import time
import psutil
from PyQt5.QtCore import pyqtSignal, QObject
from camera_input import CameraInput
import sqlite3
from Database import DatabaseHandler

class FaceRecognitionApp(QObject):
    frame_processed = pyqtSignal(np.ndarray)
    result_updated = pyqtSignal(bool)
    finished = pyqtSignal()
    def __init__(self, weights_path='./last.pt', database_path='./gestify.db'):
        super().__init__()
        self.weights_path = weights_path
        self.reference_image_path = None
        self.yolo_model = None
        self.reference_encoding = None
        self.camera = CameraInput()
        #self.cap = None

        # Database Connection
        self.database_path = database_path
        self.connection = None

        # Instantiate DatabaseHandler and call create_database
        self.database_handler = DatabaseHandler(database_path)
        self.database_handler.create_database()


        # Constants
        self.COLOR_MATCH = (0, 255, 0)
        self.COLOR_NO_MATCH = (0, 0, 255)
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX

    def load_yolo_model(self):
        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.weights_path)
            self.yolo_model.to(device).eval()
        except Exception as e:
            print(f"Error loading YOLO model: {e}")

    def load_face_encodings(self):
        return self.database_handler.load_face_encodings()

    def load_reference_encoding(self):
        reference_image = face_recognition.load_image_file(self.reference_image_path)
        self.reference_encoding = face_recognition.face_encodings(reference_image)[0]
        self.database_handler.insert_face_encoding("Reference", "Reference", self.reference_encoding.tobytes())

    def detect_faces(self, frame):
        results = self.yolo_model(frame)

        if results is not None:
            for detection in results.xyxy[0]:
                bbox = detection.cpu().numpy().astype(np.int32)
                x1, y1, x2, y2 = bbox[0:4]

                matches = self.compare_faces(self.load_reference_encoding(), self.load_face_encodings())

                if matches[0]:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLOR_MATCH, 2)
                    label = "Match"
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLOR_NO_MATCH, 2)
                    label = "No Match"

                print(f"Face at ({x1}, {y1}) - ({x2}, {y2}): {label}")
                self.result_updated.emit(matches[0])

                cv2.putText(frame, label, (x1, y1 - 10), self.FONT, 0.5, (255, 255, 255), 2)

                # Insert the face encoding into the database
                face_encoding = face_recognition.face_encodings(frame, [(y1, x2, y2, x1)])
                if face_encoding:
                    self.insert_face_encoding(face_encoding[0].tobytes())

        return frame

    def compare_faces(self, reference_encoding, face_encodings):
        matches = [face_recognition.compare_faces([reference_encoding], enc) for enc in face_encodings]
        return any(matches)

    def run_face_recognition(self):
        self.load_yolo_model()
        self.load_reference_encoding()

        self.camera.set_camera_mode("laptop")
        self.camera.set_camera()

        try:
            while True:
                start_time = time.time()

                ret, frame = self.camera.read_frame()

                detected_frame = self.detect_faces(frame)
                self.frame_processed.emit(detected_frame)

                end_time = time.time()
                processing_time = end_time - start_time
                fps = 1 / processing_time

                cpu_usage = psutil.cpu_percent()

                print(f"FPS: {fps:.2f}, Processing Time: {processing_time:.5f} seconds, CPU Usage: {cpu_usage}%")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.camera.release_camera()
            cv2.destroyAllWindows()

            self.finished.emit()