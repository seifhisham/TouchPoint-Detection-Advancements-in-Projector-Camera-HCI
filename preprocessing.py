import cv2
import numpy as np


def apply_gaussian_blur(img):
    return cv2.GaussianBlur(img, (5, 5), 0)


def find_contours(img, homography_enabled=False, homography_matrix=None):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if homography_enabled and homography_matrix is not None:
        # Apply homography mapping to each contour point
        for i in range(len(contours)):
            contours[i] = cv2.perspectiveTransform(contours[i], homography_matrix)

    # Filter contours based on area and aspect ratio
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Adjust the area threshold as needed
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.5 < aspect_ratio < 2.0:  # Adjust the aspect ratio threshold as needed
                filtered_contours.append(contour)

    cv2.drawContours(img, filtered_contours, -1, (0, 255, 0), 2)
    return img

def color_based_screen_detection(img):
    lower_color = np.array([0, 0, 100])  # Adjust the color range for projected screens
    upper_color = np.array([100, 100, 255])

    mask = cv2.inRange(img, lower_color, upper_color)
    result = cv2.bitwise_and(img, img, mask=mask)

    # Convert the result to grayscale for contour detection
    result_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(result_gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw the contours on the original image
    cv2.drawContours(img, contours, -1, (0, 0, 255), 2)

    return img

def preprocess_image(img, homography_enabled=False, homography_matrix=None, screen_detection=False):
    img_processed = apply_gaussian_blur(img)

    if screen_detection:
        img_processed = color_based_screen_detection(img_processed)
    else:
        img_processed = find_contours(img_processed, homography_enabled, homography_matrix)

    return img_processed


def histogram_equalization(img):
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)