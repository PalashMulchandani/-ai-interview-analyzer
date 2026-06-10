import cv2
import mediapipe as mp
import numpy as np
import os
import urllib.request
import time
import json
from datetime import datetime

# ── Model paths ────────────────────────────────────────────
FACE_MODEL = "face_landmarker.task"
POSE_MODEL = "pose_landmarker.task"

def download_model(url, path):
    if not os.path.exists(path):
        print(f"Downloading {path}...")
        urllib.request.urlretrieve(url, path)
        print(f"✅ {path} downloaded!")

download_model(
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
    FACE_MODEL
)
download_model(
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
    POSE_MODEL
)

# ── MediaPipe setup ────────────────────────────────────────
BaseOptions         = mp.tasks.BaseOptions
FaceLandmarker      = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
PoseLandmarker      = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode   = mp.tasks.vision.RunningMode

# ── Landmark indices ───────────────────────────────────────
# Eye contact
LEFT_IRIS         = [474, 475, 476, 477]
RIGHT_IRIS        = [469, 470, 471, 472]
LEFT_EYE_CORNERS  = [33, 133]
RIGHT_EYE_CORNERS = [362, 263]

# Expression
MOUTH_LEFT            = 61
MOUTH_RIGHT           = 291
MOUTH_TOP             = 13
MOUTH_BOTTOM          = 14
LEFT_EYEBROW_TOP      = 105
RIGHT_EYEBROW_TOP     = 334
LEFT_EYE_TOP_LID      = 159
LEFT_EYE_BOTTOM_LID   = 145
RIGHT_EYE_TOP_LID     = 386
RIGHT_EYE_BOTTOM_LID  = 374

# Posture
NOSE           = 0
LEFT_EAR       = 7
RIGHT_EAR      = 8
LEFT_SHOULDER  = 11
RIGHT_SHOULDER = 12

# ── Baseline for calibration ───────────────────────────────
baseline  = {"smile": 0.0, "eyebrow": 0.0, "eye_open": 0.0, "mouth_open": 0.0}
calibrated = False

# ── Session data ───────────────────────────────────────────
session_data = {
    "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "frames": []
}

# ══════════════════════════════════════════════════════════
#  EYE CONTACT
# ══════════════════════════════════════════════════════════

def get_eye_contact_score(landmarks):
    left_iris_x  = sum(landmarks[i].x for i in LEFT_IRIS)  / len(LEFT_IRIS)
    right_iris_x = sum(landmarks[i].x for i in RIGHT_IRIS) / len(RIGHT_IRIS)

    left_eye_left   = landmarks[LEFT_EYE_CORNERS[0]].x
    left_eye_right  = landmarks[LEFT_EYE_CORNERS[1]].x
    right_eye_left  = landmarks[RIGHT_EYE_CORNERS[0]].x
    right_eye_right = landmarks[RIGHT_EYE_CORNERS[1]].x

    left_eye_width  = abs(left_eye_right  - left_eye_left)
    right_eye_width = abs(right_eye_right - right_eye_left)

    if left_eye_width == 0 or right_eye_width == 0:
        return 0.0

    left_ratio  = (left_iris_x  - left_eye_left)  / left_eye_width
    right_ratio = (right_iris_x - right_eye_left) / right_eye_width
    avg_ratio   = (left_ratio + right_ratio) / 2

    score = 1.0 - abs(avg_ratio - 0.5) * 4
    return round(max(0.0, min(1.0, score)), 2)


# ══════════════════════════════════════════════════════════
#  POSTURE
# ══════════════════════════════════════════════════════════

def get_posture_score(landmarks):
    score    = 1.0
    penalties = []

    shoulder_diff = abs(landmarks[LEFT_SHOULDER].y - landmarks[RIGHT_SHOULDER].y)
    penalties.append(min(shoulder_diff * 5, 0.4))

    nose_x        = landmarks[NOSE].x
    shoulder_mid_x = (landmarks[LEFT_SHOULDER].x + landmarks[RIGHT_SHOULDER].x) / 2
    penalties.append(min(abs(nose_x - shoulder_mid_x) * 3, 0.3))

    ear_mid_y      = (landmarks[LEFT_EAR].y + landmarks[RIGHT_EAR].y) / 2
    shoulder_mid_y = (landmarks[LEFT_SHOULDER].y + landmarks[RIGHT_SHOULDER].y) / 2
    if ear_mid_y - shoulder_mid_y > -0.1:
        penalties.append(0.3)

    return round(max(0.0, min(1.0, 1.0 - sum(penalties))), 2)


# ══════════════════════════════════════════════════════════
#  EXPRESSION (raw helpers)
# ══════════════════════════════════════════════════════════

def smile_raw(lm):
    cy = (lm[MOUTH_TOP].y + lm[MOUTH_BOTTOM].y) / 2
    return ((cy - lm[MOUTH_LEFT].y) + (cy - lm[MOUTH_RIGHT].y)) / 2

def eyebrow_raw(lm):
    return (abs(lm[LEFT_EYEBROW_TOP].y  - lm[LEFT_EYE_TOP_LID].y) +
            abs(lm[RIGHT_EYEBROW_TOP].y - lm[RIGHT_EYE_TOP_LID].y)) / 2

def eye_open_raw(lm):
    return (abs(lm[LEFT_EYE_TOP_LID].y  - lm[LEFT_EYE_BOTTOM_LID].y) +
            abs(lm[RIGHT_EYE_TOP_LID].y - lm[RIGHT_EYE_BOTTOM_LID].y)) / 2

def mouth_open_raw(lm):
    return abs(lm[MOUTH_TOP].y - lm[MOUTH_BOTTOM].y)


def get_expression_score(landmarks):
    if not calibrated:
        return 0.5

    sd = smile_raw(landmarks)     - baseline["smile"]
    ed = eyebrow_raw(landmarks)   - baseline["eyebrow"]
    od = eye_open_raw(landmarks)  - baseline["eye_open"]
    md = mouth_open_raw(landmarks)- baseline["mouth_open"]

    s = max(0.0, min(1.0, 0.5 + sd * 10))
    e = max(0.0, min(1.0, 0.5 - ed * 15))
    o = max(0.0, min(1.0, 0.5 + od * 20))
    m = max(0.0, min(1.0, 0.5 - abs(md) * 10))

    return round(s * 0.35 + e * 0.30 + o * 0.25 + m * 0.10, 2)


def get_expression_label(landmarks):
    if not calibrated:
        return "Calibrating...", (255, 255, 0)

    sd = smile_raw(landmarks)   - baseline["smile"]
    ed = eyebrow_raw(landmarks) - baseline["eyebrow"]
    od = eye_open_raw(landmarks)- baseline["eye_open"]

    if sd > 0.005 and ed < 0.01:
        return "Confident",  (0, 255, 0)
    elif ed > 0.012:
        return "Nervous",    (0, 165, 255)
    elif od < -0.003:
        return "Tired",      (0, 0, 255)
    elif sd < -0.005:
        return "Stressed",   (0, 0, 255)
    else:
        return "Calm",       (255, 255, 0)


# ══════════════════════════════════════════════════════════
#  CALIBRATION
# ══════════════════════════════════════════════════════════

def run_calibration(cap, face_landmarker):
    global baseline, calibrated
    samples = {k: [] for k in baseline}
    start   = time.time()

    while time.time() - start < 3.0:
        ret, frame = cap.read()
        if not ret:
            continue

        remaining = 3 - int(time.time() - start)
        cv2.putText(frame, "CALIBRATION — Keep neutral face", (30, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"{remaining}s remaining...", (30, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.imshow('PrepSense — AI Interview Analyzer', frame)
        cv2.waitKey(1)

        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img    = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = face_landmarker.detect(img)

        if result.face_landmarks:
            lm = result.face_landmarks[0]
            samples["smile"].append(smile_raw(lm))
            samples["eyebrow"].append(eyebrow_raw(lm))
            samples["eye_open"].append(eye_open_raw(lm))
            samples["mouth_open"].append(mouth_open_raw(lm))

    for key in baseline:
        baseline[key] = float(np.mean(samples[key])) if samples[key] else 0.0

    calibrated = True
    print("✅ Calibration complete!")


# ══════════════════════════════════════════════════════════
#  COMBINED SCORE
# ══════════════════════════════════════════════════════════

def get_interview_score(eye, posture, expression):
    """
    Combined interview performance score
    Eye contact  → 35%
    Posture      → 30%
    Expression   → 35%
    """
    score = (eye * 0.35 + posture * 0.30 + expression * 0.35) * 100
    return round(score, 1)


def get_interview_label(score):
    if score >= 75:
        return "Excellent", (0, 255, 0)
    elif score >= 55:
        return "Good",      (0, 255, 0)
    elif score >= 35:
        return "Average",   (0, 165, 255)
    else:
        return "Needs Work",(0, 0, 255)


# ══════════════════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════════════════

def draw_dashboard(frame, eye, posture, expression,
                   interview_score, score_label, score_color,
                   expr_label, expr_color, elapsed):

    h, w = frame.shape[:2]

    # Background panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (340, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Title
    cv2.putText(frame, "PrepSense", (10, 35),
               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(frame, "AI Interview Analyzer", (10, 58),
               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    # Divider
    cv2.line(frame, (10, 68), (330, 68), (80, 80, 80), 1)

    # Individual scores
    def draw_score_bar(label, score, y, color):
        cv2.putText(frame, f"{label}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        bar_w = int(score * 200)
        cv2.rectangle(frame, (130, y - 12), (330, y - 2), (50, 50, 50), -1)
        cv2.rectangle(frame, (130, y - 12), (130 + bar_w, y - 2), color, -1)
        cv2.putText(frame, f"{int(score*100)}%", (335, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    draw_score_bar("Eye Contact",  eye,        100, (0, 255, 150))
    draw_score_bar("Posture",      posture,     125, (0, 200, 255))
    draw_score_bar("Expression",   expression,  150, (200, 100, 255))

    # Divider
    cv2.line(frame, (10, 165), (330, 165), (80, 80, 80), 1)

    # Expression label
    cv2.putText(frame, f"Mood: {expr_label}", (10, 190),
               cv2.FONT_HERSHEY_SIMPLEX, 0.55, expr_color, 2)

    # Overall score
    cv2.putText(frame, f"Interview Score", (10, 230),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
    cv2.putText(frame, f"{interview_score}/100", (10, 270),
               cv2.FONT_HERSHEY_SIMPLEX, 1.4, score_color, 3)
    cv2.putText(frame, score_label, (10, 300),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, score_color, 2)

    # Timer
    cv2.putText(frame, f"Time: {int(elapsed)}s", (10, h - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    return frame


# ══════════════════════════════════════════════════════════
#  SAVE SESSION
# ══════════════════════════════════════════════════════════

def save_session():
    if not session_data["frames"]:
        return

    frames     = session_data["frames"]
    avg_eye    = round(np.mean([f["eye_contact"]  for f in frames]), 2)
    avg_posture= round(np.mean([f["posture"]       for f in frames]), 2)
    avg_expr   = round(np.mean([f["expression"]    for f in frames]), 2)
    avg_score  = round(np.mean([f["interview_score"] for f in frames]), 1)

    summary = {
        "date":           session_data["start_time"],
        "duration_secs":  len(frames),
        "avg_eye_contact":avg_eye,
        "avg_posture":    avg_posture,
        "avg_expression": avg_expr,
        "avg_score":      avg_score,
        "frames":         frames
    }

    os.makedirs("../data", exist_ok=True)
    filename = f"../data/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Session saved: {filename}")
    print(f"   Average Score:      {avg_score}/100")
    print(f"   Avg Eye Contact:    {avg_eye}")
    print(f"   Avg Posture:        {avg_posture}")
    print(f"   Avg Expression:     {avg_expr}")


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

face_options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=FACE_MODEL),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1
)
pose_options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=POSE_MODEL),
    running_mode=VisionRunningMode.IMAGE,
    num_poses=1
)

cap        = cv2.VideoCapture(0)
start_time = None

with FaceLandmarker.create_from_options(face_options) as face_lm, \
     PoseLandmarker.create_from_options(pose_options) as pose_lm:

    # Calibrate first
    run_calibration(cap, face_lm)
    start_time = time.time()
    print("🎙️  Session started. Press Q to end and save session.\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        elapsed   = time.time() - start_time
        h, w      = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run both detectors
        face_result = face_lm.detect(mp_image)
        pose_result = pose_lm.detect(mp_image)

        eye_score  = 0.0
        expr_score = 0.0
        expr_label = "No Face"
        expr_color = (0, 0, 255)
        pose_score = 0.0

        if face_result.face_landmarks:
            lm         = face_result.face_landmarks[0]
            eye_score  = get_eye_contact_score(lm)
            expr_score = get_expression_score(lm)
            expr_label, expr_color = get_expression_label(lm)

        if pose_result.pose_landmarks:
            pose_score = get_posture_score(pose_result.pose_landmarks[0])

        interview_score              = get_interview_score(eye_score, pose_score, expr_score)
        score_label, score_color     = get_interview_label(interview_score)

        # Save frame data every second
        if int(elapsed) > len(session_data["frames"]):
            session_data["frames"].append({
                "second":          int(elapsed),
                "eye_contact":     eye_score,
                "posture":         pose_score,
                "expression":      expr_score,
                "interview_score": interview_score
            })

        # Draw dashboard
        frame = draw_dashboard(
            frame, eye_score, pose_score, expr_score,
            interview_score, score_label, score_color,
            expr_label, expr_color, elapsed
        )

        cv2.imshow('PrepSense — AI Interview Analyzer', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

cap.release()
cv2.destroyAllWindows()
save_session()
print("\nSession complete!")