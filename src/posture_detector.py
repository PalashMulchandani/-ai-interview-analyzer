import cv2
import mediapipe as mp
import numpy as np
import urllib.request
import os

# Download pose model if not exists
model_path = "pose_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading pose model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        model_path
    )
    print("Model downloaded!")

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Landmark indices we care about
NOSE           = 0
LEFT_EAR       = 7
RIGHT_EAR      = 8
LEFT_SHOULDER  = 11
RIGHT_SHOULDER = 12

def get_posture_score(landmarks):
    """
    Calculate posture score between 0.0 and 1.0
    1.0 = perfect posture
    0.0 = very bad posture
    """
    score = 1.0
    penalties = []

    # --- Check 1: Shoulder level ---
    # Both shoulders should be at same height (same y value)
    left_shoulder_y  = landmarks[LEFT_SHOULDER].y
    right_shoulder_y = landmarks[RIGHT_SHOULDER].y
    shoulder_diff = abs(left_shoulder_y - right_shoulder_y)
    # Penalize if shoulders are uneven
    shoulder_penalty = min(shoulder_diff * 5, 0.4)
    penalties.append(shoulder_penalty)

    # --- Check 2: Head position ---
    # Nose should be roughly above shoulder midpoint
    nose_x = landmarks[NOSE].x
    left_shoulder_x  = landmarks[LEFT_SHOULDER].x
    right_shoulder_x = landmarks[RIGHT_SHOULDER].x
    shoulder_mid_x = (left_shoulder_x + right_shoulder_x) / 2
    head_offset = abs(nose_x - shoulder_mid_x)
    # Penalize if head is too far left or right
    head_penalty = min(head_offset * 3, 0.3)
    penalties.append(head_penalty)

    # --- Check 3: Ear to shoulder alignment ---
    # Ears should be above shoulders (good vertical alignment)
    left_ear_y       = landmarks[LEFT_EAR].y
    right_ear_y      = landmarks[RIGHT_EAR].y
    ear_mid_y        = (left_ear_y + right_ear_y) / 2
    shoulder_mid_y   = (left_shoulder_y + right_shoulder_y) / 2
    vertical_diff    = ear_mid_y - shoulder_mid_y
    # If ears are BELOW shoulders (hunching) penalize
    if vertical_diff > -0.1:
        vertical_penalty = 0.3
    else:
        vertical_penalty = 0.0
    penalties.append(vertical_penalty)

    # Apply all penalties
    total_penalty = sum(penalties)
    score = max(0.0, min(1.0, 1.0 - total_penalty))

    return round(score, 2)


def get_score_label(score):
    """Convert score to human readable label"""
    if score >= 0.7:
        return "Good Posture", (0, 255, 0)       # Green
    elif score >= 0.4:
        return "Moderate Posture", (0, 165, 255)  # Orange
    else:
        return "Poor Posture", (0, 0, 255)        # Red


def draw_posture_lines(frame, landmarks, w, h):
    """Draw lines connecting key posture points"""
    def get_point(idx):
        return (int(landmarks[idx].x * w), int(landmarks[idx].y * h))

    # Draw shoulder line
    cv2.line(frame,
             get_point(LEFT_SHOULDER),
             get_point(RIGHT_SHOULDER),
             (255, 255, 0), 2)

    # Draw ear to shoulder lines
    cv2.line(frame,
             get_point(LEFT_EAR),
             get_point(LEFT_SHOULDER),
             (255, 0, 255), 2)
    cv2.line(frame,
             get_point(RIGHT_EAR),
             get_point(RIGHT_SHOULDER),
             (255, 0, 255), 2)

    # Draw dots on key points
    for idx in [NOSE, LEFT_EAR, RIGHT_EAR, LEFT_SHOULDER, RIGHT_SHOULDER]:
        cv2.circle(frame, get_point(idx), 5, (0, 255, 255), -1)


# Main
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_poses=1
)

print("Starting Posture Detector... Press Ctrl+C to quit")
cap = cv2.VideoCapture(0)

with PoseLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = landmarker.detect(mp_image)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            # Get posture score
            score = get_posture_score(landmarks)
            label, color = get_score_label(score)

            # Draw posture lines
            draw_posture_lines(frame, landmarks, w, h)

            # Display score
            cv2.putText(frame, f"Posture: {score}", (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            cv2.putText(frame, label, (30, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # Show individual checks
            left_shoulder_y  = landmarks[LEFT_SHOULDER].y
            right_shoulder_y = landmarks[RIGHT_SHOULDER].y
            shoulder_diff = abs(left_shoulder_y - right_shoulder_y)
            cv2.putText(frame, f"Shoulder diff: {round(shoulder_diff, 3)}", (30, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        else:
            cv2.putText(frame, "No Person Detected", (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow('Posture Detector', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Done!")