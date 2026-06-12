import streamlit as st
import requests
import time
import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

st.set_page_config(
    page_title="PrepSense — AI Interview Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0D1117; }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00FF9C, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .hero-sub {
        font-size: 1.2rem;
        color: #8B949E;
        text-align: center;
        margin-bottom: 2rem;
    }
    .question-box {
        background: linear-gradient(135deg, #1a1f2e, #161B22);
        border: 1px solid #00FF9C;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .question-text {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    .score-big {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
    }
    .metric-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .live-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #FF3B3B;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    .mode-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        transition: all 0.3s;
    }
    .tip-box {
        background: #1a1f2e;
        border-left: 4px solid #00FF9C;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #cdd9e5;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

# ── Questions bank ─────────────────────────────────────────
ALL_QUESTIONS = {
    "🎯 Behavioral": [
        "Tell me about yourself and your journey into tech",
        "Describe a time you faced a major challenge and how you overcame it",
        "Tell me about your greatest achievement so far",
        "Describe a situation where you showed leadership",
        "How do you handle working under pressure or tight deadlines?",
        "Tell me about a time you failed and what you learned",
        "Describe a conflict with a teammate and how you resolved it",
    ],
    "💻 Technical": [
        "Explain your most complex project in detail",
        "What is Object Oriented Programming and its pillars?",
        "Explain the difference between GET and POST requests",
        "What is the difference between SQL and NoSQL?",
        "Explain how machine learning models are trained",
        "What is an API and how does REST work?",
        "Explain time complexity and Big O notation",
    ],
    "🏢 HR Round": [
        "Why do you want to work at our company?",
        "Where do you see yourself in 5 years?",
        "What are your greatest strengths and weaknesses?",
        "Why should we hire you over other candidates?",
        "What motivates you to work hard?",
        "How do you keep yourself updated with new technologies?",
        "Are you comfortable working in a team environment?",
    ],
    "🚀 Situational": [
        "If you had to learn a new technology in 24 hours, how would you approach it?",
        "If your team disagreed with your technical decision, what would you do?",
        "How would you prioritize tasks if you had multiple deadlines?",
        "What would you do if you discovered a critical bug one hour before release?",
    ]
}

# ── Session state ──────────────────────────────────────────
if "mode"              not in st.session_state:
    st.session_state.mode            = None
if "session_active"    not in st.session_state:
    st.session_state.session_active  = False
if "current_question"  not in st.session_state:
    st.session_state.current_question = "Tell me about yourself and your journey into tech"
if "answer_result"     not in st.session_state:
    st.session_state.answer_result   = None
if "timer_start"       not in st.session_state:
    st.session_state.timer_start     = None


def fetch_live_scores():
    try:
        r = requests.get(f"{API_URL}/live-scores", timeout=1)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}


def get_score_color(score):
    if score >= 70:
        return "#00FF9C"
    elif score >= 50:
        return "#FFB703"
    else:
        return "#FF3B3B"


# ══════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════

def show_landing():
    st.markdown('<div class="hero-title">🎯 PrepSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">AI-Powered Interview Intelligence Platform</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="mode-card">
            <div style="font-size:4rem">🎓</div>
            <h2 style="color:#00FF9C; margin:0.5rem 0">Candidate Mode</h2>
            <p style="color:#8B949E; font-size:1rem">
                Practice mock interviews with AI feedback.<br>
                Track your improvement over time.<br>
                Get scored on eye contact, posture,<br>
                speech and answer quality.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🎓 Enter as Candidate", use_container_width=True, type="primary"):
            st.session_state.mode = "candidate"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="mode-card">
            <div style="font-size:4rem">🏢</div>
            <h2 style="color:#00B4D8; margin:0.5rem 0">Interviewer Mode</h2>
            <p style="color:#8B949E; font-size:1rem">
                Assess candidates with AI assistance.<br>
                Real-time behavioral analysis.<br>
                Auto-generated candidate reports.<br>
                Objective, bias-free scoring.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🏢 Enter as Interviewer", use_container_width=True):
            st.session_state.mode = "interviewer"
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧠 Powered By")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    techs = ["MediaPipe", "TensorFlow", "Whisper", "HuggingFace", "FastAPI", "Plotly"]
    cols  = [col1, col2, col3, col4, col5, col6]
    for col, tech in zip(cols, techs):
        with col:
            st.markdown(f"""
            <div style="background:#161B22; border:1px solid #30363D;
                        border-radius:8px; padding:0.5rem; text-align:center;
                        color:#00FF9C; font-size:0.8rem; font-weight:600;">
                {tech}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Face Landmarks", "478",   "MediaPipe tracking")
    with col2:
        st.metric("Domains",        "4",     "CV + ML + NLP + Analytics")
    with col3:
        st.metric("API Endpoints",  "10",    "REST + JWT Auth")
    with col4:
        st.metric("Mode",           "Dual",  "Candidate + Interviewer")


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
        category = st.selectbox("Category", list(ALL_QUESTIONS.keys()))
        questions = ALL_QUESTIONS[category]
        selected_q = st.selectbox("Question", questions)

        if st.button("🎲 Random Question"):
            all_q = [q for qs in ALL_QUESTIONS.values() for q in qs]
            st.session_state.current_question = random.choice(all_q)
            st.rerun()

        st.markdown("---")
        st.markdown("### 💡 STAR Method")
        st.markdown("""
        <div class="tip-box">
            <b style="color:#00FF9C">S</b>ituation — Set the context<br>
            <b style="color:#00FF9C">T</b>ask — What was your role<br>
            <b style="color:#00FF9C">A</b>ction — What did you do<br>
            <b style="color:#00FF9C">R</b>esult — What was the outcome
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎙️ Speech Tips")
        st.markdown("""
        <div class="tip-box">
            ✅ Speak at 120-150 WPM<br>
            ❌ Avoid: umm, ahh, basically<br>
            ✅ Use confident words<br>
            ❌ Avoid: I think, maybe, sort of
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 🎓 Interview Practice Mode")

    tab1, tab2, tab3 = st.tabs([
        "📹 Live Analysis",
        "💬 Answer Scorer",
        "📈 My Progress"
    ])

    # ── Tab 1: Live Analysis ──
    with tab1:
        # Current question display
        current_q = st.session_state.current_question or selected_q
        st.markdown(f"""
        <div class="question-box">
            <p style="color:#8B949E; font-size:0.9rem; margin-bottom:0.5rem">CURRENT QUESTION</p>
            <p class="question-text">"{current_q}"</p>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown('<span class="live-dot"></span>**LIVE SCORES**', unsafe_allow_html=True)

            scores = fetch_live_scores()
            eye    = int(scores.get("eye_contact",    0) * 100)
            post   = int(scores.get("posture",         0) * 100)
            expr   = int(scores.get("expression",      0) * 100)
            ivsc   = scores.get("interview_score",     0)

            # Eye contact
            eye_color = get_score_color(eye)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color:#8B949E; font-size:0.8rem">👁️ EYE CONTACT</div>
                <div style="font-size:3rem; font-weight:900; color:{eye_color}">{eye}%</div>
                <div style="background:#30363D; border-radius:4px; height:6px; margin-top:0.5rem">
                    <div style="background:{eye_color}; width:{eye}%; height:6px; border-radius:4px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Posture
            post_color = get_score_color(post)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color:#8B949E; font-size:0.8rem">🧍 POSTURE</div>
                <div style="font-size:3rem; font-weight:900; color:{post_color}">{post}%</div>
                <div style="background:#30363D; border-radius:4px; height:6px; margin-top:0.5rem">
                    <div style="background:{post_color}; width:{post}%; height:6px; border-radius:4px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Expression
            expr_color = get_score_color(expr)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color:#8B949E; font-size:0.8rem">😊 EXPRESSION</div>
                <div style="font-size:3rem; font-weight:900; color:{expr_color}">{expr}%</div>
                <div style="background:#30363D; border-radius:4px; height:6px; margin-top:0.5rem">
                    <div style="background:{expr_color}; width:{expr}%; height:6px; border-radius:4px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            # Big interview score
            ivsc_color = get_score_color(ivsc)
            st.markdown(f"""
            <div class="metric-card" style="padding:2rem">
                <div style="color:#8B949E; font-size:0.9rem">🎯 INTERVIEW SCORE</div>
                <div style="font-size:6rem; font-weight:900; color:{ivsc_color}; line-height:1">
                    {ivsc}
                </div>
                <div style="color:#8B949E; font-size:1rem">out of 100</div>
            </div>
            """, unsafe_allow_html=True)

            if ivsc >= 70:
                st.success("🟢 Excellent — Keep it up!")
            elif ivsc >= 50:
                st.warning("🟡 Average — Room to improve")
            elif ivsc > 0:
                st.error("🔴 Needs Work — Stay focused")
            else:
                st.info("Start cv_pipeline.py to see live scores")

            st.markdown("---")
            st.markdown("#### 💡 Real-time Tips")
            if eye < 50:
                st.markdown("👁️ Look directly at the camera")
            if post < 50:
                st.markdown("🧍 Sit up straight, level shoulders")
            if expr < 40:
                st.markdown("😊 Relax your face, smile naturally")
            if ivsc >= 70:
                st.markdown("✅ Great performance! Stay consistent")

        # Auto refresh
        st.markdown("---")
        auto = st.toggle("🔄 Auto Refresh (every 2s)", value=False)
        if auto:
            time.sleep(2)
            st.rerun()

    # ── Tab 2: Answer Scorer ──
    with tab2:
        current_q = st.session_state.current_question or selected_q

        st.markdown(f"""
        <div class="question-box">
            <p style="color:#8B949E; font-size:0.9rem; margin-bottom:0.5rem">ANSWER THIS QUESTION</p>
            <p class="question-text">"{current_q}"</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            answer = st.text_area(
                "Your Answer",
                placeholder="Use the STAR method:\nSituation — Task — Action — Result\n\nExample: During my college project (S), I was responsible for building the backend (T). I implemented REST APIs and optimized queries (A), which resulted in 60% faster response time (R).",
                height=200
            )

        with col2:
            st.markdown("#### Quick Tips")
            st.markdown("""
            <div class="tip-box">
                ✅ Start with situation<br>
                ✅ Use "I" statements<br>
                ✅ Give specific numbers<br>
                ✅ End with result<br>
                ❌ Don't ramble<br>
                ❌ Avoid weak words
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            analyze = st.button("🎯 Analyze Answer", type="primary", use_container_width=True)
        with col2:
            if st.button("🎲 New Random Question", use_container_width=True):
                all_q = [q for qs in ALL_QUESTIONS.values() for q in qs]
                st.session_state.current_question = random.choice(all_q)
                st.session_state.answer_result = None
                st.rerun()

        if analyze:
            if answer.strip():
                with st.spinner("🤖 AI is analyzing your answer..."):
                    try:
                        r = requests.post(
                            f"{API_URL}/score-answer",
                            json={"question": current_q, "answer": answer},
                            timeout=30
                        )
                        if r.status_code == 200:
                            st.session_state.answer_result = r.json()
                    except:
                        st.error("Cannot connect to API. Run: uvicorn api.main:app --reload")
            else:
                st.warning("Type your answer first!")

        # Show results
        if st.session_state.answer_result:
            result = st.session_state.answer_result
            st.markdown("---")
            st.markdown("### 📊 Your Results")

            col1, col2, col3, col4 = st.columns(4)
            scores_display = [
                ("Overall", result['overall_score'],    col1),
                ("Confidence", result['confidence_score'], col2),
                ("STAR", result['star_score'],           col3),
                ("Clarity", result['clarity_score'],    col4),
            ]

            for label, score, col in scores_display:
                color = get_score_color(score)
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#8B949E; font-size:0.8rem">{label}</div>
                        <div style="font-size:2.5rem; font-weight:900; color:{color}">{score}</div>
                        <div style="color:#8B949E; font-size:0.7rem">out of 100</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("#### 💡 AI Feedback")
            for f in result['feedback']:
                st.write(f)

            overall = result['overall_score']
            if overall >= 80:
                st.success("🎉 Excellent answer! You're ready for real interviews.")
            elif overall >= 60:
                st.warning("👍 Good answer. Work on the flagged areas.")
            else:
                st.error("📚 Needs improvement. Practice the STAR method more.")

    # ── Tab 3: Progress ──
    with tab3:
        st.markdown("### 📈 Your Interview Progress")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Load My Progress", type="primary"):
                try:
                    r = requests.get(f"{API_URL}/session-report", timeout=2)
                    if r.status_code == 200:
                        st.session_state.progress = r.json()
                except:
                    st.error("Start API server first!")

        if "progress" in st.session_state and st.session_state.progress:
            report = st.session_state.progress
            if "average_score" in report:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#8B949E; font-size:0.8rem">SESSIONS</div>
                        <div style="font-size:3rem; font-weight:900; color:#00FF9C">
                            {report['total_sessions']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    color = get_score_color(report['average_score'])
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#8B949E; font-size:0.8rem">AVG SCORE</div>
                        <div style="font-size:3rem; font-weight:900; color:{color}">
                            {report['average_score']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#8B949E; font-size:0.8rem">BEST SCORE</div>
                        <div style="font-size:3rem; font-weight:900; color:#00FF9C">
                            {report['best_score']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    imp = report['improvement']
                    color = "#00FF9C" if imp >= 0 else "#FF3B3B"
                    sign  = "+" if imp >= 0 else ""
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color:#8B949E; font-size:0.8rem">IMPROVEMENT</div>
                        <div style="font-size:3rem; font-weight:900; color:{color}">
                            {sign}{imp}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Session history
                try:
                    r = requests.get(f"{API_URL}/session-history", timeout=2)
                    if r.status_code == 200:
                        history = r.json()
                        if history['sessions']:
                            st.markdown("#### 📅 Session History")
                            for i, session in enumerate(history['sessions']):
                                color = get_score_color(session['score'] or 0)
                                st.markdown(f"""
                                <div style="background:#161B22; border:1px solid #30363D;
                                            border-radius:8px; padding:0.8rem 1rem;
                                            margin:0.3rem 0; display:flex;
                                            justify-content:space-between">
                                    <span style="color:#8B949E">Session {i+1} — {session['date']}</span>
                                    <span style="color:{color}; font-weight:700">
                                        {session['score']}/100
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                except:
                    pass
            else:
                st.info("No sessions yet. Run cv_pipeline.py and complete a session first!")
        else:
            st.info("Click 'Load My Progress' to see your stats")


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

        if st.button("▶️ Start Assessment", type="primary", use_container_width=True):
            try:
                r = requests.post(f"{API_URL}/start-session", timeout=2)
                if r.status_code == 200:
                    st.session_state.session_active = True
                    st.success("✅ Session started!")
            except:
                st.error("Start API server first!")

        if st.button("⏹️ End & Save", use_container_width=True):
            try:
                r = requests.post(f"{API_URL}/end-session", timeout=2)
                if r.status_code == 200:
                    st.session_state.session_active = False
                    st.success("✅ Session saved!")
            except:
                st.error("No active session")

        if st.session_state.session_active:
            st.markdown("""
            <div style="background:#1a2a1a; border:1px solid #00FF9C;
                        border-radius:8px; padding:0.8rem; text-align:center">
                <span class="live-dot"></span>
                <span style="color:#00FF9C">Assessment Live</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## 🏢 Candidate Assessment")
    st.markdown(f"**Candidate:** {candidate_name} | **Position:** {position} | **Company:** {company}")

    tab1, tab2, tab3 = st.tabs(["📊 Live Assessment", "📋 Questions", "📄 Report"])

    with tab1:
        scores = fetch_live_scores()
        eye    = int(scores.get("eye_contact",   0) * 100)
        post   = int(scores.get("posture",        0) * 100)
        expr   = int(scores.get("expression",     0) * 100)
        ivsc   = scores.get("interview_score",    0)

        col1, col2, col3 = st.columns(3)

        with col1:
            color = get_score_color(eye)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color:#8B949E">👁️ EYE CONTACT</div>
                <div style="font-size:4rem; font-weight:900; color:{color}">{eye}%</div>
                <div style="background:#30363D; border-radius:4px; height:8px">
                    <div style="background:{color}; width:{eye}%; height:8px; border-radius:4px"></div>
                </div>
                <div style="color:#8B949E; margin-top:0.5rem; font-size:0.8rem">
                    {"✅ Good" if eye > 60 else "⚠️ Looking away"}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            color = get_score_color(post)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color:#8B949E">🧍 POSTURE</div>
                <div style="font-size:4rem; font-weight:900; color:{color}">{post}%</div>
                <div style="background:#30363D; border-radius:4px; height:8px">
                    <div style="background:{color}; width:{post}%; height:8px; border-radius:4px"></div>
                </div>
                <div style="color:#8B949E; margin-top:0.5rem; font-size:0.8rem">
                    {"✅ Good" if post > 60 else "⚠️ Poor posture"}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            color = get_score_color(expr)
            st.markdown(f"""
            <div class="metric-card">
                <div style="color:#8B949E">😊 CONFIDENCE</div>
                <div style="font-size:4rem; font-weight:900; color:{color}">{expr}%</div>
                <div style="background:#30363D; border-radius:4px; height:8px">
                    <div style="background:{color}; width:{expr}%; height:8px; border-radius:4px"></div>
                </div>
                <div style="color:#8B949E; margin-top:0.5rem; font-size:0.8rem">
                    {"✅ Confident" if expr > 50 else "⚠️ Nervous"}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        ivsc_color = get_score_color(ivsc)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="padding:2rem">
                <div style="color:#8B949E">🎯 OVERALL SCORE</div>
                <div style="font-size:6rem; font-weight:900; color:{ivsc_color}">{ivsc}</div>
                <div style="color:#8B949E">out of 100</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if ivsc >= 75:
                st.success("✅ STRONG CANDIDATE — Confident, engaged, good eye contact")
            elif ivsc >= 50:
                st.warning("⚠️ AVERAGE CANDIDATE — Some areas need improvement")
            elif ivsc > 0:
                st.error("❌ WEAK PERFORMANCE — Candidate appears nervous or disengaged")
            else:
                st.info("Start cv_pipeline.py and begin assessment to see live scores")

            st.markdown("#### Real-time Observations")
            if eye < 50:
                st.markdown("• 👁️ Candidate avoiding eye contact — possible nervousness")
            if post < 50:
                st.markdown("• 🧍 Poor posture detected — slouching or tilting")
            if expr < 40:
                st.markdown("• 😊 Low confidence expression — tense facial muscles")
            if ivsc >= 70:
                st.markdown("• ✅ Strong overall presence — proceed with confidence")

        auto = st.toggle("🔄 Auto Refresh", value=False)
        if auto:
            time.sleep(2)
            st.rerun()

    with tab2:
        st.markdown("### Interview Questions")
        for category, questions in ALL_QUESTIONS.items():
            with st.expander(category):
                for q in questions:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"• {q}")
                    with col2:
                        if st.button("Ask", key=f"ask_{q[:20]}"):
                            st.session_state.current_question = q

        st.text_area("📝 Notes", placeholder="Type your notes about the candidate's answers...", height=150)

    with tab3:
        st.markdown("### 📄 Candidate Assessment Report")

        if st.button("📄 Generate Report", type="primary"):
            try:
                r = requests.get(f"{API_URL}/session-report", timeout=2)
                if r.status_code == 200:
                    report = r.json()

                    st.markdown(f"""
                    <div style="background:#161B22; border:1px solid #30363D;
                                border-radius:12px; padding:2rem; margin:1rem 0">
                        <h2 style="color:#ffffff">PrepSense Assessment Report</h2>
                        <p style="color:#8B949E">
                            <b>Candidate:</b> {candidate_name} &nbsp;|&nbsp;
                            <b>Position:</b> {position} &nbsp;|&nbsp;
                            <b>Company:</b> {company}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    if "average_score" in report:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Score",  f"{report['average_score']}/100")
                        with col2:
                            st.metric("Best Score",     f"{report['best_score']}/100")
                        with col3:
                            st.metric("Sessions Done",  report['total_sessions'])

                        score = report['average_score']
                        if score >= 75:
                            st.success("## ✅ RECOMMENDATION: HIRE")
                            st.write("Strong candidate — demonstrated confidence, good communication, professional presence.")
                        elif score >= 55:
                            st.warning("## ⚠️ RECOMMENDATION: CONSIDER")
                            st.write("Average performance — potential present but needs development in some areas.")
                        else:
                            st.error("## ❌ RECOMMENDATION: PASS")
                            st.write("Below expectations — significant improvement needed before next interview.")
                    else:
                        st.info("Complete an assessment session first!")
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