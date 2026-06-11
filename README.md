# 🎯 PrepSense — AI Interview Intelligence Platform

> An AI-powered dual-mode platform that helps candidates prepare for interviews and helps interviewers assess candidates objectively using Computer Vision, Machine Learning, NLP and Data Analytics.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Demo

> Built by a 2nd year CS student. Every line written and understood.

---

## 🎭 Dual Mode Platform

### 🎓 Candidate Mode
Practice mock interviews and get AI feedback on:
- Eye contact and gaze tracking
- Posture and body language
- Facial expression and confidence
- Answer quality using STAR method
- Speech pace and filler word detection

### 🏢 Interviewer Mode
Assess candidates objectively with:
- Real-time behavioral analysis
- Live confidence and stress scoring
- Auto-generated candidate reports
- Multi-candidate comparison
- Bias-free objective metrics

---

## 🧠 Tech Stack

| Domain | Technologies |
|--------|-------------|
| Computer Vision | MediaPipe, OpenCV |
| Machine Learning | TensorFlow, Scikit-learn |
| NLP / Speech | Whisper, HuggingFace Transformers |
| Data Analytics | Pandas, Plotly |
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit |
| Database | SQLite, JSON |
| Auth | JWT, Passlib, bcrypt |
| Deployment | Docker, Render |

---

## 📁 Project Structure
-ai-interview-analyzer/
├── src/                          # Core AI modules
│   ├── cv_pipeline.py            # Main CV pipeline
│   ├── eye_contact.py            # Eye contact detection
│   ├── posture_detector.py       # Posture analysis
│   ├── expression_detector.py    # Facial expression + calibration
│   ├── speech_detector.py        # Whisper speech transcription
│   ├── answer_scorer.py          # NLP answer quality scoring
│   └── analytics_dashboard.py   # Plotly analytics
├── api/
│   └── main.py                   # FastAPI backend
├── app/
│   └── ui.py                     # Streamlit frontend
├── data/                         # Session data (JSON)
├── model/                        # Trained models
├── tests/                        # Unit tests
├── requirements.txt
└── README.md
---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Webcam
- Microphone
- ffmpeg

### Setup

```bash
# Clone the repository
git clone https://github.com/PalashMulchandani/-ai-interview-analyzer.git
cd -ai-interview-analyzer

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run

Open 3 terminals:

**Terminal 1 — API Server:**
```bash
uvicorn api.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
streamlit run app/ui.py
```

**Terminal 3 — CV Pipeline:**
```bash
cd src
python cv_pipeline.py
```

Open browser at `http://localhost:8501`

---

## 🔑 Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Candidate | palash | pass |
| Interviewer | interviewer | pass |

---

## 📊 Features

- ✅ Real-time face landmark detection (478 points)
- ✅ Eye contact scoring using iris position tracking
- ✅ Posture analysis using shoulder/ear alignment
- ✅ Facial expression detection with personal calibration
- ✅ Speech transcription using OpenAI Whisper
- ✅ Filler word detection (umm, ahh, basically...)
- ✅ Answer quality scoring using STAR method
- ✅ Session data saved and analyzed over time
- ✅ Interactive Plotly analytics dashboard
- ✅ JWT authentication with role-based access
- ✅ Dual mode — candidate + interviewer
- ✅ REST API with auto-generated Swagger docs

---

## 🏗️ Architecture
Streamlit UI
↓
FastAPI Backend (8 endpoints)
↓
AI Modules
├── CV Pipeline (MediaPipe + OpenCV)
├── ML Models (TensorFlow)
├── Speech (Whisper)
├── NLP (HuggingFace)
└── Analytics (Pandas + Plotly)
↓
SQLite + JSON Storage
---

## 👨‍💻 Author

**Palash Mulchandani**
2nd Year Computer Science Student

- GitHub: [@PalashMulchandani](https://github.com/PalashMulchandani)

---

## 📄 License

MIT License — feel free to use and contribute.