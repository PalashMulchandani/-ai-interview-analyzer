# 🎯 PrepSense — AI Interview Intelligence Platform

> An AI-powered dual-mode platform that scores interview performance in real time using Computer Vision, Speech AI, NLP, and Data Analytics — built entirely from scratch.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)
![Whisper](https://img.shields.io/badge/Whisper-OpenAI-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 What is PrepSense?

Most interview prep tools give you questions. PrepSense gives you a real-time AI coach that watches you, listens to you, and scores you — just like a real interviewer would.

- 👁️ Tracks your eye contact using 478 face landmarks
- 🧍 Detects your posture via shoulder/ear alignment
- 😊 Reads your facial expression with personal calibration
- 🎙️ Transcribes your speech and catches filler words
- 📊 Scores your answers using the STAR method
- 📈 Shows your progress over multiple sessions

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
- Auto-generated candidate reports with HIRE/PASS recommendation
- Bias-free objective metrics

---

## 🧠 Tech Stack

| Domain | Technologies |
|--------|-------------|
| Computer Vision | MediaPipe (478 landmarks), OpenCV |
| Machine Learning | TensorFlow, Scikit-learn |
| NLP / Speech | OpenAI Whisper, HuggingFace Transformers |
| Data Analytics | Pandas, Plotly |
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit |
| Database | SQLite, JSON |
| Auth | JWT, Passlib, bcrypt |
| Deployment | Docker |

---

## 📁 Project Structure

```
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
```

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

## 📊 Features

- ✅ Real-time face landmark detection (478 points)
- ✅ Eye contact scoring using iris position tracking
- ✅ Posture analysis using shoulder/ear alignment
- ✅ Facial expression detection with personal calibration
- ✅ Speech transcription using OpenAI Whisper
- ✅ Filler word detection (umm, ahh, basically...)
- ✅ Speech pace analysis (WPM)
- ✅ Answer quality scoring using STAR method
- ✅ Session data saved and analyzed over time
- ✅ Interactive Plotly analytics dashboard embedded in Streamlit
- ✅ JWT authentication with role-based access control
- ✅ Dual mode — candidate + interviewer
- ✅ REST API with 10 endpoints and auto-generated Swagger docs
- ✅ Docker containerization

---

## 🏗️ Architecture

```
Streamlit UI
↓
FastAPI Backend (10 endpoints)
↓
AI Modules
├── CV Pipeline (MediaPipe + OpenCV)
├── ML Models (TensorFlow)
├── Speech (Whisper)
├── NLP (HuggingFace)
└── Analytics (Pandas + Plotly)
↓
SQLite + JSON Storage
```

---

## 👨‍💻 Author

**Palash Mulchandani**

CS Student who builds production-grade AI products — not tutorial projects.

PrepSense is a full-stack AI system built entirely from scratch: every module designed, every line written, every bug debugged independently. No templates, no boilerplate, no shortcuts.

Other projects:

- **CalmCampus** — AI student wellness platform
- **MoneyOS** — AI financial management platform
- **Beyond Books** — Social learning platform

> *"I don't just learn technologies — I build with them."*

- 🔗 GitHub: https://github.com/PalashMulchandani
- 💼 LinkedIn: https://www.linkedin.com/in/palash-mulchandani-29a326378/
- 📧 Open to internships and collaborations

---

## 📄 License

MIT License — feel free to use and contribute.
