import streamlit as st
import requests
import time
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="PrepSense — AI Interview Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0D1117; }
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00FF9C, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #8B949E;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

# ── Session state ──────────────────────────────────────────
if "mode"           not in st.session_state:
    st.session_state.mode           = None
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "live_scores"    not in st.session_state:
    st.session_state.live_scores    = {}


# ══════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════

def fetch_live_scores():
    try:
        r = requests.get(f"{API_URL}/live-scores", timeout=1)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}


# ══════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════

def show_landing():
    st.markdown('<div class="hero-title">🎯 PrepSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">AI-Powered Interview Intelligence Platform</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Choose Your Mode")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:#161B22; border:1px solid #30363D; border-radius:12px; padding:2rem; text-align:center;">
            <h2>🎓</h2>
            <h3 style="color:#00FF9C">Candidate Mode</h3>
            <p style="color:#8B949E">Practice mock interviews, get AI feedback,
            track your improvement over time</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Enter as Candidate", use_container_width=True, type="primary"):
            st.session_state.mode = "candidate"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background:#161B22; border:1px solid #30363D; border-radius:12px; padding:2rem; text-align:center;">
            <h2>🏢</h2>
            <h3 style="color:#00B4D8">Interviewer Mode</h3>
            <p style="color:#8B949E">Assess candidates objectively with
            AI-powered behavioral analysis</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Enter as Interviewer", use_container_width=True):
            st.session_state.mode = "interviewer"
            st.rerun()

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Domains",    "4",     "CV + ML + NLP + Analytics")
    with col2:
        st.metric("Real Time",  "30 FPS","Live analysis")
    with col3:
        st.metric("Accuracy",   "85%+",  "Confidence scoring")
    with col4:
        st.metric("Mode",       "Dual",  "Candidate + Interviewer")


# ══════════════════════════════════════════════════════════
#  CANDIDATE MODE
# ══════════════════════════════════════════════════════════

def show_candidate_mode():
    with st.sidebar:
        st.markdown("### 🎓 Candidate Mode")
        st.markdown("---")
        if st.button("🏠 Back to Home"):
            st.session_state.mode = None
            st.rerun()

        st.markdown("### 📋 Question Bank")
        questions = [
            "Tell me about yourself",
            "What is your greatest strength?",
            "Describe a challenge you faced",
            "Why do you want this job?",
            "Where do you see yourself in 5 years?",
            "Tell me about a project you built",
            "How do you handle pressure?",
            "What makes you unique?"
        ]
        selected_q = st.selectbox("Select Question", questions)

        st.markdown("---")
        st.info("Use STAR method:\n\n**S**ituation\n**T**ask\n**A**ction\n**R**esult")

    st.markdown("## 🎓 Interview Practice Mode")

    tab1, tab2, tab3 = st.tabs(["📹 Live Analysis", "💬 Answer Scorer", "📈 My Progress"])

    # ── Tab 1: Live Analysis ──
    with tab1:
        st.markdown("### Real-Time Behavior Analysis")
        st.info("Make sure cv_pipeline.py and API server are running!")

        # Auto refresh toggle
        auto_refresh = st.toggle("🔄 Auto Refresh (every 2s)", value=False)

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### Live Scores")
            scores = fetch_live_scores()

            if scores and scores.get("interview_score", 0) > 0:
                eye  = int(scores.get("eye_contact",     0) * 100)
                post = int(scores.get("posture",          0) * 100)
                expr = int(scores.get("expression",       0) * 100)
                ivsc = scores.get("interview_score", 0)

                st.metric("👁️ Eye Contact",      f"{eye}%")
                st.metric("🧍 Posture",           f"{post}%")
                st.metric("😊 Expression",        f"{expr}%")
                st.metric("🎯 Interview Score",   f"{ivsc}/100")

                # Color indicator
                if ivsc >= 70:
                    st.success(f"Score: {ivsc}/100 — Good!")
                elif ivsc >= 50:
                    st.warning(f"Score: {ivsc}/100 — Average")
                else:
                    st.error(f"Score: {ivsc}/100 — Needs Work")
            else:
                st.metric("👁️ Eye Contact",    "–")
                st.metric("🧍 Posture",         "–")
                st.metric("😊 Expression",      "–")
                st.metric("🎯 Interview Score", "–")
                st.warning("Start cv_pipeline.py to see live scores")

        with col2:
            st.markdown("#### How To Use")
            st.markdown("""
            1. Open **Terminal 1:** `uvicorn api.main:app --reload`
            2. Open **Terminal 2:** `streamlit run app/ui.py`
            3. Open **Terminal 3:** `cd src && python cv_pipeline.py`
            4. Go to `/docs` → POST `/start-session` → Execute
            5. Come back here — scores update automatically!
            """)

            st.markdown("#### Improvement Tips")
            tips = {
                "👁️ Eye Contact":  "Look directly at camera, not at your face on screen",
                "🧍 Posture":      "Sit straight, keep shoulders level and relaxed",
                "😊 Expression":   "Smile naturally, relax your eyebrows",
                "🎙️ Speech":       "Speak at 120-150 WPM, avoid filler words"
            }
            for tip, desc in tips.items():
                with st.expander(tip):
                    st.write(desc)

        # Auto refresh logic
        if auto_refresh:
            time.sleep(2)
            st.rerun()

    # ── Tab 2: Answer Scorer ──
    with tab2:
        st.markdown("### AI Answer Quality Scorer")
        st.markdown(f"**Question:** {selected_q}")

        answer = st.text_area(
            "Your Answer",
            placeholder="Type your answer using the STAR method...",
            height=150
        )

        if st.button("🎯 Analyze My Answer", type="primary"):
            if answer.strip():
                with st.spinner("Analyzing your answer..."):
                    try:
                        r = requests.post(
                            f"{API_URL}/score-answer",
                            json={"question": selected_q, "answer": answer},
                            timeout=30
                        )
                        if r.status_code == 200:
                            result = r.json()

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Overall",    f"{result['overall_score']}/100")
                            with col2:
                                st.metric("Confidence", f"{result['confidence_score']}/100")
                            with col3:
                                st.metric("STAR",       f"{result['star_score']}/100")
                            with col4:
                                st.metric("Clarity",    f"{result['clarity_score']}/100")

                            st.markdown("#### 💡 Feedback")
                            for f in result['feedback']:
                                st.write(f)

                            score = result['overall_score']
                            if score >= 80:
                                st.success("Excellent! You're ready for real interviews.")
                            elif score >= 60:
                                st.warning("Good. Work on the areas flagged above.")
                            else:
                                st.error("Needs improvement. Practice STAR method.")
                        else:
                            st.error("API error. Make sure server is running.")
                    except:
                        st.error("Cannot connect to API. Run: uvicorn api.main:app --reload")
            else:
                st.warning("Please type your answer first!")

    # ── Tab 3: Progress ──
    with tab3:
        st.markdown("### 📈 Your Progress")
        if st.button("🔄 Load Progress"):
            try:
                r = requests.get(f"{API_URL}/session-report", timeout=2)
                if r.status_code == 200:
                    report = r.json()
                    if "total_sessions" in report:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Sessions",    report['total_sessions'])
                        with col2:
                            st.metric("Avg Score",   f"{report['average_score']}/100")
                        with col3:
                            st.metric("Best Score",  f"{report['best_score']}/100")
                        with col4:
                            st.metric("Improvement", f"+{report['improvement']}")
                    else:
                        st.info("No sessions yet. Run cv_pipeline.py first!")
            except:
                st.warning("Start API server to see progress!")


# ══════════════════════════════════════════════════════════
#  INTERVIEWER MODE
# ══════════════════════════════════════════════════════════

def show_interviewer_mode():
    with st.sidebar:
        st.markdown("### 🏢 Interviewer Mode")
        st.markdown("---")
        if st.button("🏠 Back to Home"):
            st.session_state.mode = None
            st.rerun()

        st.markdown("### 👤 Candidate Info")
        candidate_name = st.text_input("Candidate Name",  "John Doe")
        position       = st.text_input("Position",        "Software Engineer")
        company        = st.text_input("Company",         "Tech Corp")

        st.markdown("---")
        st.markdown("### ⚙️ Session Control")

        if st.button("▶️ Start Assessment", type="primary"):
            try:
                r = requests.post(f"{API_URL}/start-session", timeout=2)
                if r.status_code == 200:
                    st.session_state.session_active = True
                    st.success("Session started!")
            except:
                st.error("Start API server first!")

        if st.button("⏹️ End Assessment"):
            try:
                r = requests.post(f"{API_URL}/end-session", timeout=2)
                if r.status_code == 200:
                    st.session_state.session_active = False
                    st.success("Session saved!")
            except:
                st.error("No active session")

    st.markdown("## 🏢 Candidate Assessment Mode")
    st.markdown(f"**Candidate:** {candidate_name} | **Position:** {position}")

    if st.session_state.session_active:
        st.success("🔴 Assessment in progress...")
    else:
        st.info("Click 'Start Assessment' in sidebar to begin")

    tab1, tab2, tab3 = st.tabs(["📊 Live Assessment", "📋 Question Panel", "📄 Report"])

    # ── Tab 1: Live Assessment ──
    with tab1:
        st.markdown("### Real-Time Candidate Analysis")

        auto_refresh = st.toggle("🔄 Auto Refresh", value=False)

        scores = fetch_live_scores()

        col1, col2, col3 = st.columns(3)

        with col1:
            eye = int(scores.get("eye_contact", 0) * 100)
            st.markdown("#### 👁️ Eye Contact")
            st.progress(eye / 100)
            color = "🟢" if eye > 60 else "🔴"
            st.markdown(f"### {color} {eye}%")

        with col2:
            posture = int(scores.get("posture", 0) * 100)
            st.markdown("#### 🧍 Posture")
            st.progress(posture / 100)
            color = "🟢" if posture > 60 else "🔴"
            st.markdown(f"### {color} {posture}%")

        with col3:
            expression = int(scores.get("expression", 0) * 100)
            st.markdown("#### 😊 Confidence")
            st.progress(expression / 100)
            color = "🟢" if expression > 50 else "🔴"
            st.markdown(f"### {color} {expression}%")

        overall = scores.get("interview_score", 0)
        st.markdown("---")
        st.markdown(f"## 🎯 Overall Score: **{overall}/100**")

        if overall >= 75:
            st.success("Strong candidate — confident and engaged")
        elif overall >= 50:
            st.warning("Average — some areas need improvement")
        else:
            st.error("Weak — candidate appears nervous or disengaged")

        if auto_refresh:
            time.sleep(2)
            st.rerun()

    # ── Tab 2: Question Panel ──
    with tab2:
        st.markdown("### Interview Questions")
        categories = {
            "HR Round": [
                "Tell me about yourself",
                "What are your strengths and weaknesses?",
                "Where do you see yourself in 5 years?",
                "Why do you want to work here?"
            ],
            "Technical Round": [
                "Explain OOP concepts",
                "What is the difference between GET and POST?",
                "Explain your most complex project",
                "How do you handle tight deadlines?"
            ],
            "Behavioral Round": [
                "Tell me about a time you failed",
                "Describe a conflict with a teammate",
                "Tell me about your biggest achievement",
                "How do you handle pressure?"
            ]
        }
        category = st.selectbox("Category", list(categories.keys()))
        question = st.selectbox("Question", categories[category])
        st.markdown(f"**Current Question:** {question}")
        st.text_area("Notes", placeholder="Notes about candidate's answer...", height=100)

    # ── Tab 3: Report ──
    with tab3:
        st.markdown("### Candidate Report")
        if st.button("📄 Generate Report"):
            try:
                r = requests.get(f"{API_URL}/session-report", timeout=2)
                if r.status_code == 200:
                    report = r.json()
                    st.markdown(f"## Assessment Report")
                    st.markdown(f"**Candidate:** {candidate_name} | **Position:** {position} | **Company:** {company}")
                    st.markdown("---")
                    if "average_score" in report:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Overall Score", f"{report['average_score']}/100")
                            st.metric("Best Score",    f"{report['best_score']}/100")
                        with col2:
                            st.metric("Sessions",      report['total_sessions'])
                            st.metric("Latest Score",  f"{report['latest_score']}/100")

                        score = report['average_score']
                        if score >= 75:
                            st.success("✅ RECOMMENDED — Strong candidate")
                        elif score >= 55:
                            st.warning("⚠️ CONSIDER — Average candidate")
                        else:
                            st.error("❌ NOT RECOMMENDED — Weak performance")
                    else:
                        st.info("Run an assessment session first!")
            except:
                st.error("Start API server first!")


# ══════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════

def main():
    if st.session_state.mode is None:
        show_landing()
    elif st.session_state.mode == "candidate":
        show_candidate_mode()
    elif st.session_state.mode == "interviewer":
        show_interviewer_mode()


if __name__ == "__main__":
    main()