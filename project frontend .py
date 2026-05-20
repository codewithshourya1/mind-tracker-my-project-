"""\
frontend.py \'97 MindTrack Mental Health Monitor\
================================================================================\
Run with:\
    streamlit run frontend.py --server.port 5000 --server.address 0.0.0.0\
\
Contains: Login, Register, Dashboard, Mood Tracker, Questionnaire, AI Chatbot,\
          Mood Calendar, Study Stress, Focus Mode (Pomodoro), Emergency Help.\
"""\
\
import os\
import requests\
import streamlit as st\
import plotly.graph_objects as go\
import plotly.express as px\
import pandas as pd\
from datetime import datetime\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# PAGE CONFIG  (must be the very first Streamlit call)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
st.set_page_config(\
    page_title="MindTrack \'97 Mental Health Monitor",\
    page_icon="\uc0\u55358 \u56800 ",\
    layout="wide",\
    initial_sidebar_state="auto",\
)\
\
# GLOBAL CSS\
\
st.markdown("""\
<style>\
    #MainMenu \{visibility: hidden;\}\
    footer    \{visibility: hidden;\}\
    header    \{visibility: hidden;\}\
\
    .main-title \{\
        font-size: 2.6rem; font-weight: 700; text-align: center;\
        background: linear-gradient(135deg, #6C63FF, #48D1CC);\
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;\
        margin-bottom: 0.2rem;\
    \}\
    .sub-title \{\
        text-align: center; color: #888; font-size: 1rem; margin-bottom: 1.8rem;\
    \}\
    .metric-card \{\
        background: #1E2130; border-radius: 12px; padding: 1.2rem;\
        border: 1px solid #2e3250; text-align: center;\
    \}\
    .metric-value \{ font-size: 2rem; font-weight: 700; color: #6C63FF; \}\
    .metric-label \{ font-size: 0.85rem; color: #888; margin-top: 0.2rem; \}\
    .tip-card \{\
        background: linear-gradient(135deg, #1a1a2e, #16213e);\
        border-left: 4px solid #6C63FF;\
        border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0;\
    \}\
    .user-msg \{\
        background: #2d2d4e; border-radius: 18px 18px 4px 18px;\
        padding: 0.75rem 1rem; margin: 0.4rem 0; max-width: 75%;\
        margin-left: auto; color: #FAFAFA;\
    \}\
    .bot-msg \{\
        background: #1E2130; border-radius: 18px 18px 18px 4px;\
        padding: 0.75rem 1rem; margin: 0.4rem 0; max-width: 75%;\
        border: 1px solid #2e3250; color: #FAFAFA;\
    \}\
    .chat-timestamp \{ font-size: 0.72rem; color: #555; margin: 0.1rem 0.5rem; \}\
    .advice-card \{\
        background: #1E2130; border-radius: 12px; padding: 1.2rem 1.5rem;\
        border-left: 4px solid #FFD93D; margin: 0.5rem 0;\
    \}\
    .help-card \{\
        background: #1E2130; border-radius: 12px; padding: 1.2rem 1.5rem;\
        border: 1px solid #2e3250; margin: 0.5rem 0;\
    \}\
    .help-number \{ font-size: 1.5rem; font-weight: 700; color: #6C63FF; \}\
    .help-name   \{ font-size: 1.1rem; font-weight: 600; color: #FAFAFA; \}\
    .help-desc   \{ color: #888; font-size: 0.9rem; margin-top: 0.3rem; \}\
    .help-hours  \{ color: #48D1CC; font-size: 0.85rem; margin-top: 0.2rem; \}\
    .result-card \{\
        background: #1E2130; border-radius: 12px; padding: 1.5rem;\
        border: 1px solid #2e3250; margin: 1rem 0;\
    \}\
    .stButton > button \{\
        border-radius: 8px; font-weight: 600;\
    \}\
</style>\
""", unsafe_allow_html=True)\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# API HELPER FUNCTIONS\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")\
\
\
def _auth_headers() -> dict:\
    token = st.session_state.get("token", "")\
    return \{"Authorization": f"Bearer \{token\}"\} if token else \{\}\
\
\
def api_post(endpoint: str, data: dict, auth: bool = False) -> dict | None:\
    try:\
        headers = _auth_headers() if auth else \{\}\
        r = requests.post(f"\{API_BASE\}\{endpoint\}", json=data, headers=headers, timeout=15)\
        if r.status_code == 200:\
            return r.json()\
        st.error(f"Error: \{r.json().get('detail', 'Something went wrong.')\}")\
        return None\
    except requests.exceptions.ConnectionError:\
        st.error("Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")\
        return None\
    except Exception as e:\
        st.error(f"Unexpected error: \{e\}")\
        return None\
\
\
def api_get(endpoint: str, params: dict = None) -> dict | None:\
    try:\
        r = requests.get(f"\{API_BASE\}\{endpoint\}", headers=_auth_headers(),\
                         params=params or \{\}, timeout=15)\
        if r.status_code == 200:\
            return r.json()\
        if r.status_code == 401:\
            st.warning("Session expired. Please log in again.")\
            st.session_state.clear()\
            st.rerun()\
        else:\
            st.error(f"Error: \{r.json().get('detail', 'Something went wrong.')\}")\
        return None\
    except requests.exceptions.ConnectionError:\
        st.error("Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")\
        return None\
    except Exception as e:\
        st.error(f"Unexpected error: \{e\}")\
        return None\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# SIDEBAR NAVIGATION  (only shown when logged in)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
PAGES = \{\
    "\uc0\u55357 \u56522  Dashboard":      "dashboard",\
    "\uc0\u55357 \u56541  Log Mood":        "mood",\
    "\uc0\u55357 \u56523  Questionnaire":  "questionnaire",\
    "\uc0\u55358 \u56598  MindBuddy Chat": "chatbot",\
    "\uc0\u55357 \u56517  Mood Calendar":  "calendar",\
    "\uc0\u55357 \u56538  Study Stress":   "stress",\
    "\uc0\u9201  Focus Mode":      "focus",\
    "\uc0\u55356 \u56728  Emergency Help": "emergency",\
\}\
\
if "page" not in st.session_state:\
    st.session_state["page"] = "login"\
\
\
def nav_to(page: str):\
    st.session_state["page"] = page\
    st.rerun()\
\
\
def sidebar_nav():\
    with st.sidebar:\
        st.markdown(f"### \uc0\u55357 \u56395  Hello, \{st.session_state.get('username', 'User')\}!")\
        st.markdown("---")\
        for label, key in PAGES.items():\
            if st.button(label, use_container_width=True,\
                         type="primary" if st.session_state["page"] == key else "secondary"):\
                nav_to(key)\
        st.markdown("---")\
        if st.button("\uc0\u55357 \u57002  Log Out", use_container_width=True):\
            st.session_state.clear()\
            st.session_state["page"] = "login"\
            st.rerun()\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# PAGE 0 \'97 LOGIN / REGISTER\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
def show_login():\
    col_l, col_c, col_r = st.columns([1, 2, 1])\
    with col_c:\
        st.markdown('<p class="main-title">\uc0\u55358 \u56800  MindTrack</p>', unsafe_allow_html=True)\
        st.markdown('<p class="sub-title">Your personal mental wellness companion</p>',\
                    unsafe_allow_html=True)\
\
        tab_login, tab_reg = st.tabs(["Log In", "Create Account"])\
\
        with tab_login:\
            st.markdown("#### Welcome back \uc0\u55357 \u56395 ")\
            with st.form("login_form"):\
                username = st.text_input("Username")\
                password = st.text_input("Password", type="password")\
                submitted = st.form_submit_button("Log In", use_container_width=True,\
                                                  type="primary")\
            if submitted:\
                if not username or not password:\
                    st.warning("Please fill in all fields.")\
                else:\
                    result = api_post("/auth/login", \{"username": username, "password": password\})\
                    if result:\
                        st.session_state["token"]    = result["access_token"]\
                        st.session_state["username"] = result["username"]\
                        st.session_state["page"]     = "dashboard"\
                        st.success(f"Welcome back, \{username\}! \uc0\u55356 \u57225 ")\
                        st.rerun()\
\
        with tab_reg:\
            st.markdown("#### Create your account \uc0\u55356 \u57137 ")\
            with st.form("register_form"):\
                new_user  = st.text_input("Choose a username")\
                new_email = st.text_input("Email address")\
                new_pw    = st.text_input("Create a password", type="password")\
                conf_pw   = st.text_input("Confirm password", type="password")\
                submitted_reg = st.form_submit_button("Create Account", use_container_width=True,\
                                                      type="primary")\
            if submitted_reg:\
                if not all([new_user, new_email, new_pw, conf_pw]):\
                    st.warning("Please fill in all fields.")\
                elif new_pw != conf_pw:\
                    st.error("Passwords do not match.")\
                elif len(new_pw) < 6:\
                    st.error("Password must be at least 6 characters.")\
                else:\
                    result = api_post("/auth/register",\
                                      \{"username": new_user, "email": new_email, "password": new_pw\})\
                    if result:\
                        st.success(result["message"])\
                        st.info("Now log in with your new account!")\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# PAGE 1 \'97 DASHBOARD\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
def show_dashboard():\
    st.markdown("## \uc0\u55357 \u56522  Your Dashboard")\
    st.caption("Here's how you've been feeling lately.")\
\
    data = api_get("/dashboard/summary")\
    if not data:\
        st.stop()\
\
    tip = data.get("wellness_tip", "")\
    if tip:\
        st.markdown(f'<div class="tip-card">\uc0\u55357 \u56481  <strong>Today\\'s Tip:</strong> \{tip\}</div>',\
                    unsafe_allow_html=True)\
\
    if not data.get("has_data"):\
        st.info("No mood data yet! Head to **Log Mood** to start tracking.")\
        if st.button("\uc0\u55357 \u56541  Log Your First Mood"):\
            nav_to("mood")\
        st.stop()\
\
    c1, c2, c3, c4 = st.columns(4)\
    with c1:\
        st.markdown(f'<div class="metric-card"><div class="metric-value">\{data["avg_mood"]\}/10</div>'\
                    f'<div class="metric-label">Avg Mood (7 days)</div></div>', unsafe_allow_html=True)\
    with c2:\
        st.markdown(f'<div class="metric-card"><div class="metric-value">\{data["avg_stress"]\}/10</div>'\
                    f'<div class="metric-label">Avg Stress</div></div>', unsafe_allow_html=True)\
    with c3:\
        st.markdown(f'<div class="metric-card"><div class="metric-value">\{data["avg_energy"]\}/10</div>'\
                    f'<div class="metric-label">Avg Energy</div></div>', unsafe_allow_html=True)\
    with c4:\
        st.markdown(f'<div class="metric-card"><div class="metric-value">\{data["avg_sleep"]\}h</div>'\
                    f'<div class="metric-label">Avg Sleep</div></div>', unsafe_allow_html=True)\
\
    st.markdown("")\
\
    mood_trend = data.get("mood_trend", [])\
    if mood_trend:\
        dates = [m["date"] for m in mood_trend]\
        fig = go.Figure()\
        fig.add_trace(go.Scatter(x=dates, y=[m["mood_score"]   for m in mood_trend],\
                                 name="Mood",   mode="lines+markers",\
                                 line=dict(color="#6C63FF", width=2.5), marker=dict(size=7)))\
        fig.add_trace(go.Scatter(x=da **...**\
\
_This response is too long to display in full._}
