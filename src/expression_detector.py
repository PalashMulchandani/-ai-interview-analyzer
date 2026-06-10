import cv2
import mediapipe as mp
import numpy as np
import os
import urllib.request
import time

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

# Key landmark indices
MOUTH_LEFT            = 61
MOUTH_RIGHT           = 291
MOUTH_TOP             = 13
MOUTH_BOTTOM          = 14
LEFT_EYEBROW_TOP      = 105
RIGHT_EYEBROW_TOP     = 334
LEFT_EYE_TOP          = 159
RIGHT_EYE_TOP         = 386
LEFT_EYE_TOP_LID      = 159
LEFT_EYE_BOTTOM_LID   = 145
RIGHT_EYE_TOP_LID     = 386
RIGHT_EYE_BOTTOM_LID  = 374

# ── Baseline (filled during calibration) ──────────────────
baseline = {
    "smile":      None,
    "eyebrow":    None,
    "eye_open":   None,
    "mouth_open": None,
}
calibrated = False

# ── Raw measurement helpers ────────────────────────────────

def get_mouth_smile_raw(landmarks):
    mouth_center_y = (landmarks[MOUTH_TOP].y + landmarks[MOUTH_BOTTOM].y) / 2
    left_lift      = mouth_center_y - landmarks[MOUTH_LEFT].y
    right_lift     = mouth_center_y - landmarks[MOUTH_RIGHT].y
    return (left_lift + right_lift) / 2


def get_eyebrow_raise_raw(landmarks):
    left_dist  = abs(landmarks[LEFT_EYEBROW_TOP].y  - landmarks[LEFT_EYE_TOP].y)
    right_dist = abs(landmarks[RIGHT_EYEBROW_TOP].y - landmarks[RIGHT_EYE_TOP].y)
    return (left_dist + right_dist) / 2


def get_eye_openness_raw(landmarks):
    left_open  = abs(landmarks[LEFT_EYE_TOP_LID].y  - landmarks[LEFT_EYE_BOTTOM_LID].y)
    right_open = abs(landmarks[RIGHT_EYE_TOP_LID].y - landmarks[RIGHT_EYE_BOTTOM_LID].y)
    return (left_open + right_open) / 2


def get_mouth_open_raw(landmarks):
    return abs(landmarks[MOUTH_TOP].y - landmarks[MOUTH_BOTTOM].y)


# ── Calibrated scores ──────────────────────────────────────

def get_scores(landmarks):
    """
    Returns scores relative to YOUR personal baseline.
    Positive = more than your neutral
    Negative = less than your neutral
    """
    smile_raw      = get_mouth_smile_raw(landmarks)
    eyebrow_raw    = get_eyebrow_raise_raw(landmarks)
    eye_open_raw   = get_eye_openness_raw(landmarks)
    mouth_open_raw = get_mouth_open_raw(landmarks)

    if not calibrated:
        # Before calibration just return raw values
        return smile_raw, eyebrow_raw, eye_open_raw, mouth_open_raw

    # After calibration return DIFFERENCE from baseline
    smile_delta      = smile_raw      - baseline["smile"]
    eyebrow_delta    = eyebrow_raw    - baseline["eyebrow"]
    eye_open_delta   = eye_open_raw   - baseline["eye_open"]
    mouth_open_delta = mouth_open_raw - baseline["mouth_open"]

    return smile_delta, eyebrow_delta, eye_open_delta, mouth_open_delta


def get_confidence_score(smile_d, eyebrow_d, eye_d, mouth_d):
    """
    After calibration deltas tell us change from neutral.
    Confident = slight positive smile, relaxed eyebrow,
                open eyes, controlled mouth
    """
    if not calibrated:
        return 0.5  # unknown until calibrated

    smile_score   = max(0.0, min(1.0, 0.5 + smile_d * 10))
    eyebrow_score = max(0.0, min(1.0, 0.5 - eyebrow_d * 15))
    eye_score     = max(0.0, min(1.0, 0.5 + eye_d * 20))
    mouth_score   = max(0.0, min(1.0, 0.5 - abs(mouth_d) * 10))

    confidence = (
        smile_score   * 0.35 +
        eyebrow_score * 0.30 +
        eye_score     * 0.25 +
        mouth_score   * 0.10
    )
    return round(confidence, 2)


def get_expression_label(smile_d, eyebrow_d, eye_d):
    """Determine expression based on deltas from baseline"""
    if not calibrated:
        return "Calibrating...", (255, 255, 0)

    if smile_d > 0.005 and eyebrow_d < 0.01:
        return "Confident + Smiling",   (0, 255, 0)
    elif eyebrow_d > 0.012:
        return "Nervous / Surprised",   (0, 165, 255)
    elif eye_d < -0.003:
        return "Tired / Distracted",    (0, 0, 255)
    elif smile_d < -0.005:
        return "Tense / Stressed",      (0, 0, 255)
    else:
        return "Neutral / Calm",        (255, 255, 0)


# ── Calibration ────────────────────────────────────────────

def run_calibration(cap, landmarker):
    """
    Capture 3 seconds of neutral face.
    Average the raw values → store as baseline.
    """
    global baseline, calibrated

    print("\n📸 CALIBRATION STARTING")
    print("Look at camera with your NORMAL neutral face")
    print("Collecting for 3 seconds...\n")

    samples = {k: [] for k in baseline}
    start   = time.time()

    while time.time() - start < 3.0:
        ret, frame = cap.read()
        if not ret:
            continue

        # Countdown display
        remaining = 3 - int(time.time() - start)
        h, w = frame.shape[:2]
        cv2.putText(frame, "CALIBRATING — Keep neutral face", (30, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"Starting in {remaining}s...", (30, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.imshow('Expression Detector', frame)
        cv2.waitKey(1)

        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img   = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(img)

        if result.face_landmarks:
            lm = result.face_landmarks[0]
            samples["smile"].append(get_mouth_smile_raw(lm))
            samples["eyebrow"].append(get_eyebrow_raise_raw(lm))
            samples["eye_open"].append(get_eye_openness_raw(lm))
            samples["mouth_open"].append(get_mouth_open_raw(lm))

    # Average all samples
    for key in baseline:
        if samples[key]:
            baseline[key] = float(np.mean(samples[key]))
            print(f"  Baseline {key}: {round(baseline[key], 4)}")
        else:
            baseline[key] = 0.0

    calibrated = True
    print("\n✅ Calibration complete! Starting analysis...\n")


# ── Main ───────────────────────────────────────────────────

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1
)

cap = cv2.VideoCapture(0)

with FaceLandmarker.create_from_options(options) as landmarker:

    # Run calibration first
    run_calibration(cap, landmarker)

    print("Starting Expression Detector... Press Q to quit")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result    = landmarker.detect(mp_image)

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]

            smile_d, eyebrow_d, eye_d, mouth_d = get_scores(landmarks)
            confidence = get_confidence_score(smile_d, eyebrow_d, eye_d, mouth_d)
            label, color = get_expression_label(smile_d, eyebrow_d, eye_d)

            # Display
            cv2.putText(frame, f"Expression: {label}", (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Confidence: {confidence}", (30, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Smile delta:   {round(smile_d, 4)}", (30, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(frame, f"Eyebrow delta: {round(eyebrow_d, 4)}", (30, 145),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.putText(frame, f"Eye delta:     {round(eye_d, 4)}", (30, 170),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            # Draw key points
            for idx in [MOUTH_LEFT, MOUTH_RIGHT, MOUTH_TOP,
                        MOUTH_BOTTOM, LEFT_EYEBROW_TOP, RIGHT_EYEBROW_TOP]:
                x = int(landmarks[idx].x * w)
                y = int(landmarks[idx].y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

        else:
            cv2.putText(frame, "No Face Detected", (30, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow('Expression Detector', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Done!")