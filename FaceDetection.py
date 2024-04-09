import cv2
import numpy as np
import torch
import time
import psutil
from PyQt5.QtCore import pyqtSignal, QObject
from camera_input import CameraInput
from Database import DatabaseHandler
import face_recognition

class FaceRecognitionApp(QObject):
    frame_processed = pyqtSignal(np.ndarray)
    result_updated = pyqtSignal(bool)

    def __init__(self, weights_path='../last.pt', database_path='../gestify.db'):
        super().__init__()
        self.weights_path = weights_path
        self.yolo_model = None
        self.reference_encodings = []
        self.camera = CameraInput()
        self.database_handler = DatabaseHandler(database_path=database_path)  # Initialize database handler

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

    def load_reference_encodings(self):
        reference_images = self.database_handler.load_face_images()
        if reference_images:
            self.reference_encodings = [np.array(ref[2]) for ref in reference_images]
            print(f"Loaded {len(self.reference_encodings)} reference encodings")
        else:
            print("No reference encodings loaded from the database")

    def detect_faces(self, frame):
        results = self.yolo_model(frame)

        if results is not None:
            for detection in results.xyxy[0]:
                bbox = detection.cpu().numpy().astype(np.int32)
                x1, y1, x2, y2 = bbox[0:4]

                # Extract the face region
                face_img = frame[y1:y2, x1:x2]

                # Convert face_img to RGB (required by face_recognition)
                face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

                # Find face locations and encodings in the image
                face_locations = face_recognition.face_locations(face_img_rgb)
                face_encodings = face_recognition.face_encodings(face_img_rgb, face_locations)

                for face_location, face_encoding in zip(face_locations, face_encodings):
                    top, right, bottom, left = face_location

                    label = "No Match"  # Default label
                    match = False

                    if len(face_encoding) == 256:
                        # Compare the detected face encoding with each reference encoding
                        match = self.compare_faces(face_encoding)
                        if match:
                            label = "Match"

                    print(f"Face at ({x1}, {y1}) - ({x2}, {y2}): {label}, {match}")
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLOR_MATCH if match else self.COLOR_NO_MATCH, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), self.FONT, 0.5, (255, 255, 255), 2)

        return frame

    def compare_faces(self, detected_face_encoding):
        try:
            if self.reference_encodings:
                # Compare the detected face encoding with each reference encoding
                matches = face_recognition.compare_faces(self.reference_encodings, detected_face_encoding)
                if True in matches:
                    return True
        except Exception as e:
            print(f"Error comparing faces: {e}")
        return False

    def run_face_recognition(self):
        try:
            self.load_yolo_model()
            self.load_reference_encodings()

            self.camera.set_camera_mode("laptop")
            self.camera.set_camera()

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