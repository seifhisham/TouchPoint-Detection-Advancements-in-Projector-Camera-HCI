import os
import cv2
import numpy as np
import torch
import time
import psutil
from PyQt5.QtCore import pyqtSignal, QObject
from camera_input import CameraInput
import face_recognition


class FaceRecognitionApp(QObject):
    frame_processed = pyqtSignal(np.ndarray)
    result_updated = pyqtSignal(bool)

    def __init__(self, weights_path='../last.pt', faces_folder='../uploaded_faces'):
        super().__init__()
        self.weights_path = weights_path
        self.yolo_model = None
        self.reference_encodings = []
        self.camera = CameraInput()

        # Constants
        self.COLOR_MATCH = (0, 255, 0)
        self.COLOR_NO_MATCH = (0, 0, 255)
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX

        self.faces_folder = faces_folder

    def load_yolo_model(self):
        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.weights_path)
            self.yolo_model.to(device).eval()
        except Exception as e:
            print(f"Error loading YOLO model: {e}")

    def load_reference_encodings_from_folder(self):
        try:
            self.reference_encodings = []
            for filename in os.listdir(self.faces_folder):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    img_path = os.path.join(self.faces_folder, filename)
                    face_img = face_recognition.load_image_file(img_path)
                    face_encoding = face_recognition.face_encodings(face_img)
                    if len(face_encoding) > 0:
                        self.reference_encodings.append(face_encoding[0])
            print(f"Loaded {len(self.reference_encodings)} reference encodings from folder: {self.faces_folder}")
        except Exception as e:
            print(f"Error loading reference encodings: {e}")

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

                face_encodings = face_recognition.face_encodings(face_img_rgb)

                for face_encodings in face_encodings:
                    label = "No Match"  # Default label

                    match = self.compare_faces(face_encodings)
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
            self.load_reference_encodings_from_folder()

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
