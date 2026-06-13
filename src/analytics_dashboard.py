import json
import os
import glob
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
def build_dashboard_streamlit(sessions_df, frames_df):
    latest_date   = sessions_df['date'].iloc[-1]
    latest_frames = frames_df[frames_df['session_date'] == latest_date].copy()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "📈 Score Over Time",
            "📊 Avg Scores by Category",
            "👁️ Eye Contact Timeline",
            "🏆 Session History"
        ),
        vertical_spacing=0.18,
        horizontal_spacing=0.12
    )

    fig.add_trace(go.Scatter(
        x=latest_frames['second'], y=latest_frames['interview_score'],
        mode='lines+markers', line=dict(color='#00FF9C', width=2), marker=dict(size=4)
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=['Eye Contact', 'Posture', 'Expression'],
        y=[sessions_df['avg_eye'].mean()*100, sessions_df['avg_posture'].mean()*100, sessions_df['avg_expression'].mean()*100],
        marker_color=['#00B4D8', '#90E0EF', '#CAF0F8'],
        text=[f"{v:.1f}%" for v in [sessions_df['avg_eye'].mean()*100, sessions_df['avg_posture'].mean()*100, sessions_df['avg_expression'].mean()*100]],
        textposition='auto'
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=latest_frames['second'], y=latest_frames['eye_contact'],
        mode='lines', line=dict(color='#FFB703', width=2),
        fill='tozeroy', fillcolor='rgba(255,183,3,0.15)'
    ), row=2, col=1)

    if len(sessions_df) > 1:
        fig.add_trace(go.Scatter(
            x=list(range(1, len(sessions_df)+1)), y=sessions_df['avg_score'],
            mode='lines+markers', line=dict(color='#FB5607', width=2), marker=dict(size=8)
        ), row=2, col=2)
    else:
        fig.add_trace(go.Bar(
            x=latest_frames['second'], y=latest_frames['posture'], marker_color='#8338EC'
        ), row=2, col=2)

    fig.update_layout(
        paper_bgcolor='#0D1117', plot_bgcolor='#161B22',
        font=dict(color='white'), showlegend=False, height=680,
        margin=dict(t=60, b=20, l=20, r=20)
    )
    fig.update_xaxes(gridcolor='#30363D')
    fig.update_yaxes(gridcolor='#30363D')
    return fig

# ── Load all session files ─────────────────────────────────

def load_all_sessions():
    """Load all JSON session files from data folder"""
    session_files = glob.glob("../data/session_*.json")

    if not session_files:
        print("❌ No session files found. Run cv_pipeline.py first!")
        return None, None

    all_sessions = []
    all_frames   = []

    for file in sorted(session_files):
        with open(file, "r") as f:
            session = json.load(f)

        # Session summary
        all_sessions.append({
            "date":            session["date"],
            "duration":        session["duration_secs"],
            "avg_eye":         session["avg_eye_contact"],
            "avg_posture":     session["avg_posture"],
            "avg_expression":  session["avg_expression"],
            "avg_score":       session["avg_score"]
        })

        # Frame by frame data
        for frame in session["frames"]:
            frame["session_date"] = session["date"]
            all_frames.append(frame)

    sessions_df = pd.DataFrame(all_sessions)
    frames_df   = pd.DataFrame(all_frames)

    print(f"✅ Loaded {len(all_sessions)} session(s)")
    print(f"✅ Total frames: {len(all_frames)}")
    return sessions_df, frames_df


# ── Analysis ───────────────────────────────────────────────

def analyze_performance(sessions_df, frames_df):
    """Generate insights from session data"""
    print("\n" + "="*50)
    print("📊 PREPSENSE PERFORMANCE REPORT")
    print("="*50)

    # Overall stats
    print(f"\n📅 Total Sessions:     {len(sessions_df)}")
    print(f"⏱️  Total Practice Time: {sessions_df['duration'].sum()} seconds")
    print(f"\n🎯 AVERAGE SCORES:")
    print(f"   Interview Score:  {sessions_df['avg_score'].mean():.1f}/100")
    print(f"   Eye Contact:      {sessions_df['avg_eye'].mean():.2f}")
    print(f"   Posture:          {sessions_df['avg_posture'].mean():.2f}")
    print(f"   Expression:       {sessions_df['avg_expression'].mean():.2f}")

    # Best session
    best_idx     = sessions_df['avg_score'].idxmax()
    best_session = sessions_df.loc[best_idx]
    print(f"\n🏆 BEST SESSION:")
    print(f"   Date:  {best_session['date']}")
    print(f"   Score: {best_session['avg_score']}/100")

    # Weakest area
    avg_eye  = sessions_df['avg_eye'].mean()
    avg_post = sessions_df['avg_posture'].mean()
    avg_expr = sessions_df['avg_expression'].mean()

    weakest = min(
        [("Eye Contact", avg_eye),
         ("Posture",     avg_post),
         ("Expression",  avg_expr)],
        key=lambda x: x[1]
    )

    strongest = max(
        [("Eye Contact", avg_eye),
         ("Posture",     avg_post),
         ("Expression",  avg_expr)],
        key=lambda x: x[1]
    )

    print(f"\n💪 STRONGEST AREA: {strongest[0]} ({strongest[1]:.2f})")
    print(f"⚠️  WEAKEST AREA:   {weakest[0]} ({weakest[1]:.2f})")

    # Improvement suggestions
    print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
    if avg_eye < 0.6:
        print("   → Practice looking directly at camera while speaking")
    if avg_post < 0.6:
        print("   → Sit straight, keep shoulders level")
    if avg_expr < 0.5:
        print("   → Smile naturally, relax your eyebrows")
    if sessions_df['avg_score'].mean() >= 70:
        print("   → Great performance! Keep practicing consistency")

    print("\n" + "="*50)


# ── Charts ─────────────────────────────────────────────────

def build_dashboard(sessions_df, frames_df):
    """Build interactive Plotly dashboard"""

    # Get latest session frames
    latest_date   = sessions_df['date'].iloc[-1]
    latest_frames = frames_df[frames_df['session_date'] == latest_date].copy()

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "📈 Interview Score Over Time (per second)",
            "📊 Average Scores by Category",
            "👁️ Eye Contact Timeline",
            "🏆 Session History"
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # ── Chart 1: Score over time (latest session) ──
    fig.add_trace(
        go.Scatter(
            x=latest_frames['second'],
            y=latest_frames['interview_score'],
            mode='lines+markers',
            name='Interview Score',
            line=dict(color='#00FF9C', width=2),
            marker=dict(size=4)
        ),
        row=1, col=1
    )

    # ── Chart 2: Average scores bar chart ──
    categories = ['Eye Contact', 'Posture', 'Expression']
    averages   = [
        sessions_df['avg_eye'].mean() * 100,
        sessions_df['avg_posture'].mean() * 100,
        sessions_df['avg_expression'].mean() * 100
    ]
    colors = ['#00B4D8', '#90E0EF', '#CAF0F8']

    fig.add_trace(
        go.Bar(
            x=categories,
            y=averages,
            name='Avg Score %',
            marker_color=colors,
            text=[f"{v:.1f}%" for v in averages],
            textposition='auto'
        ),
        row=1, col=2
    )

    # ── Chart 3: Eye contact timeline ──
    fig.add_trace(
        go.Scatter(
            x=latest_frames['second'],
            y=latest_frames['eye_contact'],
            mode='lines',
            name='Eye Contact',
            line=dict(color='#FFB703', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 183, 3, 0.2)'
        ),
        row=2, col=1
    )

    # ── Chart 4: Session history ──
    if len(sessions_df) > 1:
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(sessions_df) + 1)),
                y=sessions_df['avg_score'],
                mode='lines+markers',
                name='Session Score',
                line=dict(color='#FB5607', width=2),
                marker=dict(size=8)
            ),
            row=2, col=2
        )
    else:
        # Only one session — show category breakdown
        fig.add_trace(
            go.Bar(
                x=latest_frames['second'],
                y=latest_frames['posture'],
                name='Posture',
                marker_color='#8338EC'
            ),
            row=2, col=2
        )

    # ── Layout ──
    fig.update_layout(
        title=dict(
            text="🎯 PrepSense — AI Interview Performance Dashboard",
            font=dict(size=20, color='white')
        ),
        paper_bgcolor='#0D1117',
        plot_bgcolor='#161B22',
        font=dict(color='white'),
        showlegend=False,
        height=700
    )

    # Update axes
    fig.update_xaxes(gridcolor='#30363D', zerolinecolor='#30363D')
    fig.update_yaxes(gridcolor='#30363D', zerolinecolor='#30363D')

    # Save and open
    output_path = "../data/dashboard.html"
    fig.write_html(output_path)
    print(f"\n✅ Dashboard saved: {output_path}")
    print("Opening in browser...")

    import webbrowser
    webbrowser.open(os.path.abspath(output_path))


# ── Main ───────────────────────────────────────────────────

if __name__ == "__main__":
    # Make sure we're reading from right place
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    sessions_df, frames_df = load_all_sessions()

    if sessions_df is not None:
        analyze_performance(sessions_df, frames_df)
        build_dashboard(sessions_df, frames_df) 