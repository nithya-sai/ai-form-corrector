import numpy as np
import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Global variables to track rep state across frames
counter = 0
stage = None

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def analyze_frame_with_mediapipe(frame):
    global counter, stage
    
    # 1. Convert the incoming OpenCV frame to RGB for MediaPipe
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
  
    # 2. Process pose detection
    results = pose.process(image)
  
    # 3. Convert back to BGR
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    form_message = "Tracking..."

    try:
        landmarks = results.pose_landmarks.landmark
        
        # ==========================================
        # PASTE YOUR JOINT EXTRACTION & COUNTER LOGIC HERE
        # ==========================================
        # Example using calculate_angle (adjust landmarks to your exercise):
        # shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        # elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        # wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        # angle = calculate_angle(shoulder, elbow, wrist)
        #
        # if angle > 160:
        #     stage = "down"
        # if angle < 30 and stage == 'down':
        #     stage = "up"
        #     counter += 1
        
        form_message = "Good Form"

    except Exception as e:
        form_message = "Align with camera"

    return counter, form_message