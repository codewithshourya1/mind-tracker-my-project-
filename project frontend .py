"""
frontend.py — MindTrack Mental Health Monitor
================================================================================
Run with:
    streamlit run frontend.py --server.port 5000 --server.address 0.0.0.0

Contains: Login, Register, Dashboard, Mood Tracker, Questionnaire, AI Chatbot,
          Mood Calendar, Study Stress, Focus Mode (Pomodoro), Emergency Help.
"""

import os
import time
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# =============================================================================
# PAGE CONFIG  (must be the very first Streamlit call)
# =============================================================================

st.set_page_config(
    page_title="MindTrack — Mental Health Monitor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto",
)

# =============================================================================
# GLOBAL CSS
# =============================================================================

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer    {visibility: hidden;}
    header    {visibility: hidden;}

    .main-title {
        font-size: 2.6rem; font-weight: 700; text-align: center;
        background: linear-gradient(135deg, #6C63FF, #48D1CC);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center; color: #888; font-size: 1rem; margin-bottom: 1.8rem;
    }
    .metric-card {
        background: #1E2130; border-radius: 12px; padding: 1.2rem;
        border: 1px solid #2e3250; text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #6C63FF; }
    .metric-label { font-size: 0.85rem; color: #888; margin-top: 0.2rem; }
    .tip-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 4px solid #6C63FF;
        border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0;
    }
    .user-msg {
        background: #2d2d4e; border-radius: 18px 18px 4px 18px;
        padding: 0.75rem 1rem; margin: 0.4rem 0; max-width: 75%;
        margin-left: auto; color: #FAFAFA;
    }
    .bot-msg {
        background: #1E2130; border-radius: 18px 18px 18px 4px;
        padding: 0.75rem 1rem; margin: 0.4rem 0; max-width: 75%;
        border: 1px solid #2e3250; color: #FAFAFA;
    }
    .chat-timestamp { font-size: 0.72rem; color: #555; margin: 0.1rem 0.5rem; }
    .advice-card {
        background: #1E2130; border-radius: 12px; padding: 1.2rem 1.5rem;
        border-left: 4px solid #FFD93D; margin: 0.5rem 0;
    }
    .help-card {
        background: #1E2130; border-radius: 12px; padding: 1.2rem 1.5rem;
        border: 1px solid #2e3250; margin: 0.5rem 0;
    }
    .help-number { font-size: 1.5rem; font-weight: 700; color: #6C63FF; }
    .help-name   { font-size: 1.1rem; font-weight: 600; color: #FAFAFA; }
    .help-desc   { color: #888; font-size: 0.9rem; margin-top: 0.3rem; }
    .help-hours  { color: #48D1CC; font-size: 0.85rem; margin-top: 0.2rem; }
    .result-card {
        background: #1E2130; border-radius: 12px; padding: 1.5rem;
        border: 1px solid #2e3250; margin: 1rem 0;
    }
    .stButton > button {
        border-radius: 8px; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# API HELPER FUNCTIONS
# =============================================================================

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def _auth_headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_post(endpoint: str, data: dict, auth: bool = False) -> dict | None:
    try:
        headers = _auth_headers() if auth else {}
        r = requests.post(f"{API_BASE}{endpoint}", json=data, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        st.error(f"Error: {r.json().get('detail', 'Something went wrong.')}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend. Make sure the API server is running.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_get(endpoint: str, params: dict = None) -> dict | None:
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=_auth_headers(),
                         params=params or {}, timeout=15)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 401:
            st.warning("Session expired. Please log in again.")
            st.session_state.clear()
            st.rerun()
        else:
            st.error(f"Error: {r.json().get('detail', 'Something went wrong.')}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend. Make sure the API server is running.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

PAGES = {
    "📊  Dashboard":      "dashboard",
    "😊  Log Mood":        "mood",
    "📋  Questionnaire":  "questionnaire",
    "🤖  MindBuddy Chat": "chatbot",
    "📅  Mood Calendar":  "calendar",
    "📖  Study Stress":   "stress",
    "⏱  Focus Mode":      "focus",
    "🆘  Emergency Help": "emergency",
}

if "page" not in st.session_state:
    st.session_state["page"] = "login"


def nav_to(page: str):
    st.session_state["page"] = page
    st.rerun()


def sidebar_nav():
    with st.sidebar:
        st.markdown(f"### 👋  Hello, {st.session_state.get('username', 'User')}!")
        st.markdown("---")
        for label, key in PAGES.items():
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state["page"] == key else "secondary"):
                nav_to(key)
        st.markdown("---")
        if st.button("🚪  Log Out", use_container_width=True):
            st.session_state.clear()
            st.session_state["page"] = "login"
            st.rerun()


# =============================================================================
# PAGE 0 — LOGIN / REGISTER
# =============================================================================

def show_login():
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<p class="main-title">🧠  MindTrack</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Your personal mental wellness companion</p>',
                    unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["Log In", "Create Account"])

        with tab_login:
            st.markdown("#### Welcome back 👋")
            with st.form("login_form"):
                username  = st.text_input("Username")
                password  = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True,
                                                  type="primary")
            if submitted:
                if not username or not password:
                    st.warning("Please fill in all fields.")
                else:
                    result = api_post("/auth/login", {"username": username, "password": password})
                    if result:
                        st.session_state["token"]    = result["access_token"]
                        st.session_state["username"] = result["username"]
                        st.session_state["page"]     = "dashboard"
                        st.success(f"Welcome back, {username}! 🎉")
                        st.rerun()

        with tab_reg:
            st.markdown("#### Create your account 🌱")
            with st.form("register_form"):
                new_user      = st.text_input("Choose a username")
                new_email     = st.text_input("Email address")
                new_pw        = st.text_input("Create a password", type="password")
                conf_pw       = st.text_input("Confirm password", type="password")
                submitted_reg = st.form_submit_button("Create Account", use_container_width=True,
                                                      type="primary")
            if submitted_reg:
                if not all([new_user, new_email, new_pw, conf_pw]):
                    st.warning("Please fill in all fields.")
                elif new_pw != conf_pw:
                    st.error("Passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    result = api_post("/auth/register",
                                      {"username": new_user, "email": new_email, "password": new_pw})
                    if result:
                        st.success(result["message"])
                        st.info("Now log in with your new account!")


# =============================================================================
# PAGE 1 — DASHBOARD
# =============================================================================

def show_dashboard():
    st.markdown("## 📊  Your Dashboard")
    st.caption("Here's how you've been feeling lately.")

    data = api_get("/dashboard/summary")
    if not data:
        st.stop()

    tip = data.get("wellness_tip", "")
    if tip:
        st.markdown(f'<div class="tip-card">💡  <strong>Today\'s Tip:</strong> {tip}</div>',
                    unsafe_allow_html=True)

    if not data.get("has_data"):
        st.info("No mood data yet! Head to **Log Mood** to start tracking.")
        if st.button("😊  Log Your First Mood"):
            nav_to("mood")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{data["avg_mood"]}/10</div>'
                    f'<div class="metric-label">Avg Mood (7 days)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{data["avg_stress"]}/10</div>'
                    f'<div class="metric-label">Avg Stress</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{data["avg_energy"]}/10</div>'
                    f'<div class="metric-label">Avg Energy</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{data["avg_sleep"]}h</div>'
                    f'<div class="metric-label">Avg Sleep</div></div>', unsafe_allow_html=True)

    st.markdown("")

    mood_trend = data.get("mood_trend", [])
    if mood_trend:
        dates = [m["date"] for m in mood_trend]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=[m["mood_score"]   for m in mood_trend],
                                 name="Mood",   mode="lines+markers",
                                 line=dict(color="#6C63FF", width=2.5), marker=dict(size=7)))
        fig.add_trace(go.Scatter(x=dates, y=[m["stress_level"] for m in mood_trend],
                                 name="Stress", mode="lines+markers",
                                 line=dict(color="#FF6B6B", width=2.5), marker=dict(size=7)))
        fig.add_trace(go.Scatter(x=dates, y=[m["energy_level"] for m in mood_trend],
                                 name="Energy", mode="lines+markers",
                                 line=dict(color="#48D1CC", width=2.5), marker=dict(size=7)))
        fig.update_layout(
            title="Mood Trend (last 14 days)",
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="#FAFAFA"),
            xaxis=dict(gridcolor="#2e3250"),
            yaxis=dict(gridcolor="#2e3250", range=[0, 10]),
            legend=dict(bgcolor="#1E2130"),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        mood_dist = data.get("mood_distribution", {})
        if mood_dist:
            fig2 = px.pie(
                names=list(mood_dist.keys()),
                values=list(mood_dist.values()),
                title="Mood Distribution",
                color_discrete_sequence=px.colors.sequential.Plasma,
            )
            fig2.update_layout(
                plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                font=dict(color="#FAFAFA"), height=300,
            )
            st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        sentiment_trend = data.get("sentiment_trend", [])
        if sentiment_trend:
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=[s["date"] for s in sentiment_trend],
                y=[s["sentiment"] for s in sentiment_trend],
                marker_color=["#6C63FF" if s["sentiment"] >= 0 else "#FF6B6B"
                              for s in sentiment_trend],
            ))
            fig3.update_layout(
                title="Journal Sentiment",
                plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                font=dict(color="#FAFAFA"),
                xaxis=dict(gridcolor="#2e3250"),
                yaxis=dict(gridcolor="#2e3250", range=[-1, 1]),
                height=300,
            )
            st.plotly_chart(fig3, use_container_width=True)

    latest = data.get("latest_assessment")
    if latest:
        st.markdown("---")
        st.markdown(f"**Latest Assessment:** {latest['category'].title()} — "
                    f"Severity: `{latest['severity']}` | Score: `{latest['score']}`")


# =============================================================================
# PAGE 2 — LOG MOOD
# =============================================================================

def show_mood():
    st.markdown("## 😊  Log Your Mood")
    st.caption("How are you feeling right now?")

    MOOD_OPTIONS = {
        "😄 Happy":       ("Happy",       9),
        "😊 Good":        ("Good",        7),
        "😐 Neutral":     ("Neutral",     5),
        "😔 Sad":         ("Sad",         3),
        "😰 Anxious":     ("Anxious",     3),
        "😤 Frustrated":  ("Frustrated",  4),
        "😴 Tired":       ("Tired",       4),
        "🤩 Excited":     ("Excited",     9),
    }

    with st.form("mood_form"):
        st.markdown("#### Select your mood")
        mood_choice = st.selectbox("How are you feeling?", list(MOOD_OPTIONS.keys()))

        col1, col2, col3 = st.columns(3)
        with col1:
            energy_level = st.slider("Energy Level", 1, 10, 5,
                                     help="1 = exhausted, 10 = full of energy")
        with col2:
            stress_level = st.slider("Stress Level", 1, 10, 5,
                                     help="1 = very calm, 10 = extremely stressed")
        with col3:
            sleep_hours  = st.slider("Sleep Hours Last Night", 0.0, 12.0, 7.0, step=0.5)

        journal_note = st.text_area("Journal Note (optional)",
                                    placeholder="What's on your mind today?",
                                    height=120)

        submitted = st.form_submit_button("Log Mood 📝", use_container_width=True, type="primary")

    if submitted:
        mood_label, mood_score = MOOD_OPTIONS[mood_choice]
        payload = {
            "mood_score":    mood_score,
            "mood_label":    mood_label,
            "energy_level":  energy_level,
            "stress_level":  stress_level,
            "journal_note":  journal_note,
            "sleep_hours":   sleep_hours,
        }
        result = api_post("/mood/log", payload, auth=True)
        if result:
            st.success("Mood logged successfully! 🎉")
            st.balloons()

    st.markdown("---")
    st.markdown("### Recent Mood History")
    history = api_get("/mood/history", params={"limit": 10})
    if history and history.get("moods"):
        df = pd.DataFrame(history["moods"])
        df["date"] = pd.to_datetime(df["date"])
        df = df[["date", "mood_label", "mood_score", "energy_level",
                 "stress_level", "sleep_hours", "sentiment_label"]].sort_values("date", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No mood entries yet.")


# =============================================================================
# PAGE 3 — QUESTIONNAIRE
# =============================================================================

def show_questionnaire():
    st.markdown("## 📋  Mental Health Questionnaire")
    st.caption("Answer honestly — your responses are private.")

    category = st.selectbox(
        "Select assessment type",
        ["general", "stress", "anxiety", "burnout"],
        format_func=lambda x: x.title(),
    )

    q_data = api_get(f"/questionnaire/questions/{category}")
    if not q_data:
        st.stop()

    questions = q_data.get("questions", [])
    answers = {}

    with st.form("questionnaire_form"):
        for q in questions:
            ans = st.radio(q["text"], q["options"], horizontal=True, key=q["id"])
            answers[q["id"]] = q["options"].index(ans)

        submitted = st.form_submit_button("Submit Assessment", use_container_width=True,
                                          type="primary")

    if submitted:
        result = api_post("/questionnaire/submit",
                          {"answers": answers, "category": category}, auth=True)
        if result:
            severity = result["severity"]
            color    = {"Low": "#48D1CC", "Moderate": "#FFD93D", "High": "#FF6B6B"}.get(severity, "#888")
            st.markdown(
                f'<div class="result-card">'
                f'<h3 style="color:{color}">Severity: {severity}</h3>'
                f'<p>Score: {result["score"]} / {result["max_score"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("#### Recommendations")
            for rec in result["recommendations"]:
                st.markdown(
                    f'<div class="advice-card">💡 {rec}</div>',
                    unsafe_allow_html=True,
                )
            if result.get("follow_up_categories"):
                st.info(f"Consider also taking: "
                        f"{', '.join(r.title() for r in result['follow_up_categories'])} assessments.")


# =============================================================================
# PAGE 4 — CHATBOT
# =============================================================================

def show_chatbot():
    st.markdown("## 🤖  MindBuddy Chat")
    st.caption("Your compassionate AI mental health companion.")

    history = api_get("/chatbot/history", params={"limit": 20})
    chats   = history.get("chats", []) if history else []

    chat_container = st.container()
    with chat_container:
        if not chats:
            st.markdown(
                '<div class="bot-msg">👋 Hi! I\'m MindBuddy. How are you feeling today? '
                'I\'m here to listen and support you.</div>',
                unsafe_allow_html=True,
            )
        for chat in chats:
            ts = chat.get("created_at", "")[:16].replace("T", " ")
            st.markdown(f'<div class="user-msg">{chat["user_message"]}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="chat-timestamp" style="text-align:right">{ts}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="bot-msg">🤖 {chat["bot_reply"]}</div>',
                        unsafe_allow_html=True)

    st.markdown("---")
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_msg = st.text_input("Message MindBuddy...", label_visibility="collapsed")
        with col_btn:
            send = st.form_submit_button("Send 💬", use_container_width=True, type="primary")

    if send and user_msg.strip():
        result = api_post("/chatbot/send", {"message": user_msg}, auth=True)
        if result:
            st.rerun()


# =============================================================================
# PAGE 5 — MOOD CALENDAR
# =============================================================================

def show_calendar():
    st.markdown("## 📅  Mood Calendar")
    st.caption("Your mood history at a glance.")

    data = api_get("/dashboard/calendar")
    if not data or not data.get("calendar"):
        st.info("No mood entries yet. Start logging your mood!")
        return

    calendar = data["calendar"]
    MOOD_COLORS = {
        "Happy":       "#48D1CC",
        "Good":        "#6C63FF",
        "Excited":     "#FFD93D",
        "Neutral":     "#888888",
        "Tired":       "#A0A0C0",
        "Sad":         "#FF6B6B",
        "Anxious":     "#FF8C42",
        "Frustrated":  "#C0392B",
        "Study Check-in": "#48D1CC",
    }

    rows = {}
    for date_str, info in calendar.items():
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            week = d.strftime("%Y-W%W")
            rows.setdefault(week, {})[d.strftime("%a")] = info
        except ValueError:
            continue

    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for week, day_data in sorted(rows.items(), reverse=True):
        cols = st.columns(7)
        for i, day in enumerate(days_order):
            with cols[i]:
                if day in day_data:
                    info  = day_data[day]
                    color = MOOD_COLORS.get(info["mood_label"], "#6C63FF")
                    st.markdown(
                        f'<div style="background:{color}; border-radius:8px; padding:0.5rem; '
                        f'text-align:center; margin:2px;">'
                        f'<small>{day}</small><br>'
                        f'<strong>{info["mood_score"]}/10</strong><br>'
                        f'<small style="font-size:0.7rem">{info["mood_label"]}</small>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="background:#1E2130; border-radius:8px; padding:0.5rem; '
                        f'text-align:center; margin:2px; border:1px solid #2e3250;">'
                        f'<small style="color:#555">{day}</small><br>'
                        f'<span style="color:#333">—</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


# =============================================================================
# PAGE 6 — STUDY STRESS
# =============================================================================

def show_study_stress():
    st.markdown("## 📖  Study Stress Check-in")
    st.caption("Let's assess your current academic workload.")

    with st.form("stress_form"):
        col1, col2 = st.columns(2)
        with col1:
            exams        = st.number_input("Exams this week", min_value=0, max_value=10, value=1)
            assignments  = st.number_input("Assignments pending", min_value=0, max_value=20, value=2)
            sleep_hours  = st.slider("Sleep hours last night", 0.0, 12.0, 6.5, step=0.5)
        with col2:
            study_hours  = st.slider("Study hours per day", 0.0, 16.0, 4.0, step=0.5)
            overwhelmed  = st.checkbox("I'm feeling overwhelmed right now")
            notes        = st.text_area("Any notes?", placeholder="Optional...", height=80)

        submitted = st.form_submit_button("Check My Stress Level", use_container_width=True,
                                          type="primary")

    if submitted:
        payload = {
            "exams_this_week":      exams,
            "assignments_pending":  assignments,
            "sleep_hours":          sleep_hours,
            "study_hours_per_day":  study_hours,
            "feeling_overwhelmed":  overwhelmed,
            "notes":                notes,
        }
        result = api_post("/wellness/study-stress", payload, auth=True)
        if result:
            level  = result["stress_level"]
            score  = result["stress_score"]
            colors = {"Low": "#48D1CC", "Moderate": "#FFD93D", "High": "#FF6B6B"}
            color  = colors.get(level, "#888")
            st.markdown(
                f'<div class="result-card">'
                f'<h3 style="color:{color}">Stress Level: {level} (Score: {score})</h3>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("#### Advice")
            for tip in result["advice"]:
                st.markdown(f'<div class="advice-card">💡 {tip}</div>', unsafe_allow_html=True)


# =============================================================================
# PAGE 7 — FOCUS MODE (POMODORO)
# =============================================================================

def show_focus():
    st.markdown("## ⏱  Focus Mode — Pomodoro Timer")
    st.caption("Stay focused with structured work and break intervals.")

    col1, col2, col3 = st.columns(3)
    with col1:
        work_mins  = st.number_input("Work duration (mins)",  min_value=1, max_value=60, value=25)
    with col2:
        break_mins = st.number_input("Break duration (mins)", min_value=1, max_value=30, value=5)
    with col3:
        sessions   = st.number_input("Number of sessions",   min_value=1, max_value=10, value=4)

    if "pomodoro_running"   not in st.session_state:
        st.session_state["pomodoro_running"]   = False
    if "pomodoro_session"   not in st.session_state:
        st.session_state["pomodoro_session"]   = 0
    if "pomodoro_phase"     not in st.session_state:
        st.session_state["pomodoro_phase"]     = "work"
    if "pomodoro_end_time"  not in st.session_state:
        st.session_state["pomodoro_end_time"]  = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶  Start Focus Session", use_container_width=True, type="primary",
                     disabled=st.session_state["pomodoro_running"]):
            st.session_state["pomodoro_running"]  = True
            st.session_state["pomodoro_session"]  = 1
            st.session_state["pomodoro_phase"]    = "work"
            st.session_state["pomodoro_end_time"] = time.time() + work_mins * 60
            st.rerun()
    with col_stop:
        if st.button("⏹  Stop", use_container_width=True,
                     disabled=not st.session_state["pomodoro_running"]):
            st.session_state["pomodoro_running"] = False
            st.rerun()

    if st.session_state["pomodoro_running"]:
        end_time    = st.session_state["pomodoro_end_time"]
        remaining   = max(0, int(end_time - time.time()))
        phase       = st.session_state["pomodoro_phase"]
        session_num = st.session_state["pomodoro_session"]

        mins, secs  = divmod(remaining, 60)
        color       = "#6C63FF" if phase == "work" else "#48D1CC"
        label       = "🎯 Work Time" if phase == "work" else "☕ Break Time"

        st.markdown(
            f'<div style="text-align:center; padding:2rem;">'
            f'<h2 style="color:{color}">{label}</h2>'
            f'<h1 style="font-size:4rem; color:{color}">{mins:02d}:{secs:02d}</h1>'
            f'<p>Session {session_num} of {sessions}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if remaining == 0:
            if phase == "work":
                if session_num >= sessions:
                    st.success("🎉 All sessions complete! Great work!")
                    st.session_state["pomodoro_running"] = False
                else:
                    st.session_state["pomodoro_phase"]    = "break"
                    st.session_state["pomodoro_end_time"] = time.time() + break_mins * 60
            else:
                st.session_state["pomodoro_session"]  += 1
                st.session_state["pomodoro_phase"]     = "work"
                st.session_state["pomodoro_end_time"]  = time.time() + work_mins * 60

        time.sleep(1)
        st.rerun()
    else:
        st.markdown("""
        **How Pomodoro works:**
        1. 🎯 Work focused for your set duration
        2. ☕ Take a short break
        3. 🔄 Repeat for all sessions
        4. 🎉 Celebrate your productivity!
        """)


# =============================================================================
# PAGE 8 — EMERGENCY HELP
# =============================================================================

def show_emergency():
    st.markdown("## 🆘  Emergency Mental Health Resources")
    st.markdown(
        '<div style="background:#2d1a1a; border-left:4px solid #FF6B6B; '
        'border-radius:8px; padding:1rem 1.5rem; margin-bottom:1.5rem;">'
        '❤️ <strong>You are not alone.</strong> Reaching out for help is a sign of strength. '
        'If you are in immediate danger, please call emergency services (112).'
        '</div>',
        unsafe_allow_html=True,
    )

    data = api_get("/wellness/emergency")
    if not data:
        st.stop()

    for res in data.get("resources", []):
        st.markdown(
            f'<div class="help-card">'
            f'<div class="help-name">{res["name"]}</div>'
            f'<div class="help-number">📞 {res["number"]}</div>'
            f'<div class="help-desc">{res["description"]}</div>'
            f'<div class="help-hours">🕐 {res["hours"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🧘  Immediate Coping Techniques")
    with st.expander("4-7-8 Breathing Exercise"):
        st.markdown("""
        1. Breathe in through your nose for **4 seconds**
        2. Hold your breath for **7 seconds**
        3. Exhale completely through your mouth for **8 seconds**
        4. Repeat 3–4 times
        """)
    with st.expander("5-4-3-2-1 Grounding Technique"):
        st.markdown("""
        Name:
        - **5** things you can **see**
        - **4** things you can **touch**
        - **3** things you can **hear**
        - **2** things you can **smell**
        - **1** thing you can **taste**
        """)
    with st.expander("Progressive Muscle Relaxation"):
        st.markdown("""
        Starting from your toes, tense each muscle group for 5 seconds, then release.
        Work your way up: feet → legs → stomach → hands → arms → shoulders → face.
        """)


# =============================================================================
# MAIN ROUTER
# =============================================================================

def main():
    page = st.session_state.get("page", "login")

    if page == "login":
        show_login()
        return

    if not st.session_state.get("token"):
        st.session_state["page"] = "login"
        st.rerun()

    sidebar_nav()

    if page == "dashboard":
        show_dashboard()
    elif page == "mood":
        show_mood()
    elif page == "questionnaire":
        show_questionnaire()
    elif page == "chatbot":
        show_chatbot()
    elif page == "calendar":
        show_calendar()
    elif page == "stress":
        show_study_stress()
    elif page == "focus":
        show_focus()
    elif page == "emergency":
        show_emergency()
    else:
        nav_to("dashboard")


if __name__ == "__main__" or True:
    main()
