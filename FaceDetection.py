import cv2
import numpy as np
import torch
import face_recognition

# Constants
WEIGHTS_PATH = './face_detection_yolov5s.pt'
REFERENCE_IMAGE_PATH = './seif2.jpg'
COLOR_MATCH = (0, 255, 0)
COLOR_NO_MATCH = (0, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX

def load_yolo_model(weights_path):
    try:
        yolo = torch.hub.load('ultralytics/yolov5', 'custom', path=weights_path)
        return yolo
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return None

def compare_faces(reference_encoding, face_encodings):
    # Compare face encodings with the reference image encoding
    matches = face_recognition.compare_faces([reference_encoding], face_encodings[0] if face_encodings else None)
    return matches

def detect_faces(frame, yolo_model, reference_encoding):
    # Detect faces using YOLO
    results = yolo_model(frame)

    # Draw bounding boxes around faces
    if results is not None:
        for detection in results.xyxy[0]:
            bbox = detection.cpu().numpy().astype(np.int32)
            x1, y1, x2, y2 = bbox[0:4]

            # Use face recognition to compare with the reference image
            matches = compare_faces(reference_encoding, face_recognition.face_encodings(frame, [(y1, x2, y2, x1)]))

            # Draw bounding box only if there is a match
            if matches[0]:
                cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_MATCH, 2)
                label = "Match"
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_NO_MATCH, 2)
                label = "No Match"

            # Display result
            cv2.putText(frame, label, (x1, y1 - 10), FONT, 0.5, (255, 255, 255), 2)

    return frame

def main():
    yolo_model = load_yolo_model(WEIGHTS_PATH)
    if yolo_model is None:
        return

    # Load the reference image for face comparison
    reference_image = face_recognition.load_image_file(REFERENCE_IMAGE_PATH)
    reference_encoding = face_recognition.face_encodings(reference_image)[0]

    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()

            # Detect faces and perform face recognition
            detected_frame = detect_faces(frame, yolo_model, reference_encoding)
            cv2.imshow('Face Recognition', detected_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
