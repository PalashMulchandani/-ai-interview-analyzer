from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
import glob
from datetime import datetime
import numpy as np

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from answer_scorer import analyze_answer

# ── FastAPI app ────────────────────────────────────────────
app = FastAPI(
    title="PrepSense API",
    description="AI Interview Performance Analyzer",
    version="1.0.0"
)

# ── CORS — allows frontend to talk to backend ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Session storage ────────────────────────────────────────
current_session = {
    "active":    False,
    "start_time": None,
    "scores":    []
}

# ── Request models ─────────────────────────────────────────
class AnswerRequest(BaseModel):
    question: str
    answer:   str

class ScoreUpdate(BaseModel):
    eye_contact:      float
    posture:          float
    expression:       float
    interview_score:  float

# ══════════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════════

@app.get("/health")
def health_check():
    """Check if API is running"""
    return {
        "status":  "running",
        "message": "PrepSense API is live!",
        "version": "1.0.0"
    }


@app.post("/start-session")
def start_session():
    """Start a new interview session"""
    global current_session
    current_session = {
        "active":     True,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scores":     []
    }
    return {
        "status":  "started",
        "message": "Interview session started!",
        "time":    current_session["start_time"]
    }


@app.post("/end-session")
def end_session():
    """End current session and save"""
    global current_session

    if not current_session["active"]:
        raise HTTPException(status_code=400, detail="No active session")

    current_session["active"] = False

    # Calculate averages
    scores = current_session["scores"]
    if scores:
        summary = {
            "date":            current_session["start_time"],
            "duration_secs":   len(scores),
            "avg_eye_contact": round(np.mean([s["eye_contact"]     for s in scores]), 2),
            "avg_posture":     round(np.mean([s["posture"]          for s in scores]), 2),
            "avg_expression":  round(np.mean([s["expression"]       for s in scores]), 2),
            "avg_score":       round(np.mean([s["interview_score"]  for s in scores]), 1),
            "frames":          scores
        }

        # Save to data folder
        os.makedirs("../data", exist_ok=True)
        filename = f"../data/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(summary, f, indent=2)

        return {
            "status":    "saved",
            "summary":   summary,
            "file":      filename
        }

    return {"status": "ended", "message": "No scores recorded"}


@app.post("/update-scores")
def update_scores(scores: ScoreUpdate):
    """Update live CV scores from pipeline"""
    if not current_session["active"]:
        raise HTTPException(status_code=400, detail="No active session")

    frame_data = {
        "second":          len(current_session["scores"]),
        "eye_contact":     scores.eye_contact,
        "posture":         scores.posture,
        "expression":      scores.expression,
        "interview_score": scores.interview_score
    }
    current_session["scores"].append(frame_data)

    return {"status": "updated", "frame": frame_data}


@app.get("/live-scores")
def get_live_scores():
    """Get current live scores"""
    if not current_session["scores"]:
        return {
            "eye_contact":     0.0,
            "posture":         0.0,
            "expression":      0.0,
            "interview_score": 0.0
        }

    latest = current_session["scores"][-1]
    return latest


@app.post("/score-answer")
def score_answer(request: AnswerRequest):
    """Score an interview answer"""
    if not request.question or not request.answer:
        raise HTTPException(status_code=400, detail="Question and answer required")

    result = analyze_answer(request.question, request.answer)

    return {
        "status":           "scored",
        "overall_score":    result["overall_score"],
        "confidence_score": result["confidence_score"],
        "star_score":       result["star_score"],
        "clarity_score":    result["clarity_score"],
        "sentiment_score":  result["sentiment_score"],
        "feedback":         result["feedback"]
    }


@app.get("/session-history")
def get_session_history():
    """Get all past sessions"""
    session_files = glob.glob("../data/session_*.json")
    sessions      = []

    for file in sorted(session_files):
        with open(file, "r") as f:
            session = json.load(f)
        sessions.append({
            "date":      session.get("date"),
            "score":     session.get("avg_score"),
            "duration":  session.get("duration_secs")
        })

    return {
        "total_sessions": len(sessions),
        "sessions":       sessions
    }


@app.get("/session-report")
def get_session_report():
    """Get analytics report of all sessions"""
    session_files = glob.glob("../data/session_*.json")

    if not session_files:
        return {"message": "No sessions found"}

    all_scores = []
    for file in session_files:
        with open(file, "r") as f:
            session = json.load(f)
        all_scores.append(session.get("avg_score", 0))

    return {
        "total_sessions":  len(session_files),
        "average_score":   round(np.mean(all_scores), 1),
        "best_score":      round(max(all_scores), 1),
        "latest_score":    round(all_scores[-1], 1),
        "improvement":     round(all_scores[-1] - all_scores[0], 1) if len(all_scores) > 1 else 0
    }