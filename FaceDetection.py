import cv2
import numpy as np
import torch
import os
from ultralytics import YOLO


def load_yolo_model(weights_path):
    try:
        yolo = torch.hub.load('ultralytics/yolov5', 'custom', path=weights_path)
        return yolo
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return None


def detect_faces(frame, yolo_model):
    # Detect faces using YOLO
    results = yolo_model(frame)

    # Draw bounding boxes around faces
    if results is not None:
        for detection in results.xyxy[0]:
            bbox = detection.cpu().numpy().astype(np.int32)  # Convert to NumPy array
            x1, y1, x2, y2 = bbox[0:4]  # Extract coordinates
            confidence = float(detection[4])  # Confidence score

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Display object name and confidence above the bounding box
            label = f"{yolo_model.names[int(detection[5])]}: {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return frame




def main():
    #weights_path = 'D:/study/University/Graduation project/Touch Projector/sample codes/yolov5-master/runs/train/exp26/weights'
    weights_path = './last.pt'
    #weights_path = 'C:/Users/aseif/PycharmProjects/TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/last.pt'
    # Load the YOLO face detection model
    yolo_model = load_yolo_model(weights_path)
    if yolo_model is None:
        return

    # Capture frames from the webcam
    cap = cv2.VideoCapture(0)

    try:
        while True:
            # Capture the frame
            ret, frame = cap.read()

            # Detect faces and display the frame
            detected_frame = detect_faces(frame, yolo_model)
            cv2.imshow('Detected Faces', detected_frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Release the video capture and destroy windows
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
