import cv2
import mediapipe as mp
import urllib.request
import os

# Download model if not exists
model_path = "face_landmarker.task"
if not os.path.exists(model_path):
    print("Downloading model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        model_path
    )

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Eye landmark indices
LEFT_IRIS  = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_EYE_CORNERS  = [33, 133]
RIGHT_EYE_CORNERS = [362, 263]

def get_eye_contact_score(landmarks, frame_w, frame_h):
    """
    Calculate eye contact score between 0.0 and 1.0
    1.0 = perfect eye contact
    0.0 = looking completely away
    """

    # Get iris center (average of iris landmarks)
    left_iris_x = sum(landmarks[i].x for i in LEFT_IRIS) / len(LEFT_IRIS)
    right_iris_x = sum(landmarks[i].x for i in RIGHT_IRIS) / len(RIGHT_IRIS)

    # Get eye corner positions
    left_eye_left   = landmarks[LEFT_EYE_CORNERS[0]].x
    left_eye_right  = landmarks[LEFT_EYE_CORNERS[1]].x
    right_eye_left  = landmarks[RIGHT_EYE_CORNERS[0]].x
    right_eye_right = landmarks[RIGHT_EYE_CORNERS[1]].x

    # Calculate how centered iris is in eye (0.5 = perfectly centered)
    left_eye_width  = abs(left_eye_right - left_eye_left)
    right_eye_width = abs(right_eye_right - right_eye_left)

    # Avoid division by zero
    if left_eye_width == 0 or right_eye_width == 0:
        return 0.0

    left_ratio  = (left_iris_x - left_eye_left) / left_eye_width
    right_ratio = (right_iris_x - right_eye_left) / right_eye_width

    # Average ratio of both eyes
    avg_ratio = (left_ratio + right_ratio) / 2

    # Score: closer to 0.5 = better eye contact
    score = 1.0 - abs(avg_ratio - 0.5) * 4
    score = max(0.0, min(1.0, score))

    return round(score, 2)


def get_score_label(score):
    """Convert score to human readable label"""
    if score >= 0.7:
        return "Good Eye Contact", (0, 255, 0)      # Green
    elif score >= 0.4:
        return "Moderate Eye Contact", (0, 165, 255) # Orange
    else:
        return "Poor Eye Contact", (0, 0, 255)       # Red


# Main — run this file directly to test
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1
)

print("Starting Eye Contact Detector... Press Q to quit")
cap = cv2.VideoCapture(0)

with FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = landmarker.detect(mp_image)

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]

            # Get eye contact score
            score = get_eye_contact_score(landmarks, w, h)
            label, color = get_score_label(score)

            # Display score on screen
            cv2.putText(frame, f"Eye Contact: {score}", (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            cv2.putText(frame, label, (30, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # Draw iris dots
            for idx in LEFT_IRIS + RIGHT_IRIS:
                x = int(landmarks[idx].x * w)
                y = int(landmarks[idx].y * h)
                cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)

        else:
            cv2.putText(frame, "No Face Detected", (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow('Eye Contact Detector', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Done!")