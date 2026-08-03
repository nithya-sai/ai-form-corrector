import cv2
import numpy as np
# Import mediapipe if you use it here
# import mediapipe as mp

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def analyze_frame_with_mediapipe(frame):
    # 1. Add your MediaPipe processing on the single 'frame' here
    # 2. Extract landmarks, calculate angles using calculate_angle(), update your rep counter
    
    # Example dummy return values (replace these with your actual rep count and form status):
    current_reps = 0
    form_message = "Good Form"
    
    return current_reps, form_message