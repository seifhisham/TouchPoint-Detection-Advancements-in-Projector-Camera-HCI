import numpy as np
import cv2


def calibrate_homography(img, screen_points):
    # Display the image and get user input for screen points
    cv2.imshow("Calibration Image", img)
    screen_pts = []

    def get_mouse_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            screen_pts.append((x, y))
            if len(screen_pts) == 4:
                cv2.destroyWindow("Calibration Image")

    cv2.setMouseCallback("Calibration Image", get_mouse_click)

    while True:
        cv2.imshow("Calibration Image", img)
        if cv2.waitKey(1) & 0xFF == 27:  # Break the loop on 'Esc' key
            break

    screen_points.extend(screen_pts)
    # Define corresponding points in the image
    img_pts = np.array([[0, 0], [img.shape[1], 0], [img.shape[1], img.shape[0]], [0, img.shape[0]]], dtype=np.float32)

    # Calculate homography matrix
    h, _ = cv2.findHomography(img_pts, np.array(screen_pts, dtype=np.float32))

    cv2.destroyWindow("Calibration Image")
    return h
