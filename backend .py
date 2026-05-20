{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 """\
backend.py \'97 MindTrack Mental Health Monitor \
=============================================================================\
Run with:\
    uvicorn backend:app --host 0.0.0.0 --port 8000 --reload\
\
Contains: Database, Auth, Sentiment, Schemas, and all API routes.\
"""\
\
# \uc0\u9472 \u9472  Imports \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \u9472 \
import os\
import json\
import sqlite3\
import random\
import bcrypt\
from pathlib import Path\
from datetime import datetime, timedelta\
from typing import Optional\
\
from fastapi import FastAPI, HTTPException, Header, status\
from fastapi.middleware.cors import CORSMiddleware\
from pydantic import BaseModel\
from textblob import TextBlob\
from jose import JWTError, jwt\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# DATABASE SETUP\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
DB_PATH = Path(__file__).parent / "data" / "mindtrack.db"\
DB_PATH.parent.mkdir(exist_ok=True)\
\
\
def get_connection() -> sqlite3.Connection:\
    conn = sqlite3.connect(str(DB_PATH))\
    conn.row_factory = sqlite3.Row\
    conn.execute("PRAGMA journal_mode=WAL")\
    return conn\
\
\
def init_db():\
    conn = get_connection()\
    cur = conn.cursor()\
\
    cur.execute("""\
        CREATE TABLE IF NOT EXISTS users (\
            id          INTEGER PRIMARY KEY AUTOINCREMENT,\
            username    TEXT UNIQUE NOT NULL,\
            email       TEXT UNIQUE NOT NULL,\
            password    TEXT NOT NULL,\
            created_at  TEXT NOT NULL\
        )""")\
\
    cur.execute("""\
        CREATE TABLE IF NOT EXISTS moods (\
            id              INTEGER PRIMARY KEY AUTOINCREMENT,\
            username        TEXT NOT NULL,\
            mood_score      INTEGER NOT NULL,\
            mood_label      TEXT NOT NULL,\
            energy_level    INTEGER NOT NULL,\
            stress_level    INTEGER NOT NULL,\
            journal_note    TEXT DEFAULT '',\
            sleep_hours     REAL DEFAULT 7.0,\
            sentiment_score REAL DEFAULT 0.0,\
            sentiment_label TEXT DEFAULT 'Neutral',\
            date            TEXT NOT NULL,\
            created_at      TEXT NOT NULL\
        )""")\
\
    cur.execute("""\
        CREATE TABLE IF NOT EXISTS chats (\
            id           INTEGER PRIMARY KEY AUTOINCREMENT,\
            username     TEXT NOT NULL,\
            user_message TEXT NOT NULL,\
            bot_reply    TEXT NOT NULL,\
            created_at   TEXT NOT NULL\
        )""")\
\
    cur.execute("""\
        CREATE TABLE IF NOT EXISTS questionnaires (\
            id           INTEGER PRIMARY KEY AUTOINCREMENT,\
            username     TEXT NOT NULL,\
            category     TEXT NOT NULL,\
            score        INTEGER NOT NULL,\
            max_score    INTEGER NOT NULL,\
            severity     TEXT NOT NULL,\
            answers_json TEXT NOT NULL,\
            created_at   TEXT NOT NULL\
        )""")\
\
    conn.commit()\
    conn.close()\
    print("\uc0\u9989  SQLite database ready at:", DB_PATH)\
\
\
init_db()\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# AUTH UTILITIES\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
SECRET_KEY = os.getenv("SECRET_KEY", "mindtrack-secret-key-change-in-production-2024")\
ALGORITHM = "HS256"\
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours\
\
\
def hash_password(plain: str) -> str:\
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()\
\
\
def verify_password(plain: str, hashed: str) -> bool:\
    return bcrypt.checkpw(plain.encode(), hashed.encode())\
\
\
def create_access_token(data: dict) -> str:\
    payload = data.copy()\
    payload["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)\
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)\
\
\
def decode_token(token: str) -> dict | None:\
    try:\
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])\
    except JWTError:\
        return None\
\
\
def get_current_user(authorization: str = Header(None)) -> str:\
    if not authorization or not authorization.startswith("Bearer "):\
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")\
    payload = decode_token(authorization.split(" ")[1])\
    if not payload:\
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")\
    return payload["sub"]\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# SENTIMENT ANALYSIS  (TextBlob)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
def analyze_sentiment(text: str) -> float:\
    if not text or not text.strip():\
        return 0.0\
    return round(TextBlob(text).sentiment.polarity, 3)\
\
\
def get_sentiment_label(score: float) -> str:\
    if score >= 0.3:\
        return "Positive"\
    if score <= -0.3:\
        return "Negative"\
    return "Neutral"\
\
\
WELLNESS_TIPS = [\
    "Take a 5-minute walk outside \'97 fresh air clears the mind.",\
    "Drink a glass of water right now. Hydration affects mood!",\
    "Write down 3 things you're grateful for today.",\
    "Do a 2-minute deep breathing exercise: in for 4, hold for 4, out for 4.",\
    "Text a friend or family member something positive today.",\
    "Step away from your screen for 10 minutes and stretch.",\
    "Listen to your favourite song without doing anything else.",\
    "Eat something nutritious \'97 your brain needs fuel!",\
    "Set one small, achievable goal for today.",\
    "Remind yourself: it's okay not to be perfect.",\
    "Try the 5-4-3-2-1 grounding technique: name 5 things you see.",\
    "Celebrate a small win from this week.",\
    "Get 7-8 hours of sleep tonight \'97 it's medicine.",\
    "Limit social media to 30 minutes today.",\
    "Practice saying no to one non-essential commitment.",\
]\
\
\
def get_wellness_tip() -> str:\
    return random.choice(WELLNESS_TIPS)\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# PYDANTIC SCHEMAS\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
class UserRegister(BaseModel):\
    username: str\
    email: str\
    password: str\
\
\
class UserLogin(BaseModel):\
    username: str\
    password: str\
\
\
class TokenResponse(BaseModel):\
    access_token: str\
    token_type: str = "bearer"\
    username: str\
\
\
class MoodEntry(BaseModel):\
    mood_score: int\
    mood_label: str\
    energy_level: int\
    stress_level: int\
    journal_note: Optional[str] = ""\
    sleep_hours: Optional[float] = 7.0\
\
\
class QuestionnaireAnswer(BaseModel):\
    answers: dict\
    category: str\
\
\
class ChatMessage(BaseModel):\
    message: str\
\
\
class StudyStressEntry(BaseModel):\
    exams_this_week: int\
    assignments_pending: int\
    sleep_hours: float\
    study_hours_per_day: float\
    feeling_overwhelmed: bool\
    notes: Optional[str] = ""\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# FASTAPI APP\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
app = FastAPI(\
    title="MindTrack Mental Health Monitor API",\
    description="Student mental health tracking backend \'97 single file version",\
    version="1.0.0",\
)\
\
app.add_middleware(\
    CORSMiddleware,\
    allow_origins=["*"],\
    allow_credentials=True,\
    allow_methods=["*"],\
    allow_headers=["*"],\
)\
\
\
@app.get("/")\
def root():\
    return \{"status": "running", "app": "MindTrack API", "version": "1.0.0"\}\
\
\
@app.get("/health")\
def health():\
    return \{"status": "ok"\}\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# AUTH ROUTES  (/auth/register  /auth/login)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
@app.post("/auth/register")\
def register_user(user: UserRegister):\
    conn = get_connection()\
    try:\
        existing = conn.execute(\
            "SELECT id FROM users WHERE username = ? OR email = ?",\
            (user.username, user.email)\
        ).fetchone()\
        if existing:\
            raise HTTPException(status_code=400, detail="Username or email already registered.")\
        conn.execute(\
            "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",\
            (user.username, user.email, hash_password(user.password), datetime.utcnow().isoformat())\
        )\
        conn.commit()\
    finally:\
        conn.close()\
    return \{"message": f"Account created successfully! Welcome, \{user.username\} \uc0\u55356 \u57225 "\}\
\
\
@app.post("/auth/login", response_model=TokenResponse)\
def login_user(user: UserLogin):\
    conn = get_connection()\
    try:\
        db_user = conn.execute(\
            "SELECT username, password FROM users WHERE username = ?", (user.username,)\
        ).fetchone()\
    finally:\
        conn.close()\
    if not db_user or not verify_password(user.password, db_user["password"]):\
        raise HTTPException(status_code=401, detail="Invalid username or password.")\
    token = create_access_token(\{"sub": user.username\})\
    return TokenResponse(access_token=token, token_type="bearer", username=user.username)\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# MOOD ROUTES  (/mood/log  /mood/history  /mood/stats)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
@app.post("/mood/log")\
def log_mood(entry: MoodEntry, authorization: str = Header(None)):\
    username = get_current_user(authorization)\
    s_score = analyze_sentiment(entry.journal_note or "")\
    s_label = get_sentiment_label(s_score)\
    now = datetime.utcnow()\
    conn = get_connection()\
    try:\
        conn.execute(\
            """INSERT INTO moods\
               (username, mood_score, mood_label, energy_level, stress_level,\
                journal_note, sleep_hours, sentiment_score, sentiment_label, date, created_at)\
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",\
            (username, entry.mood_score, entry.mood_label, entry.energy_level,\
             entry.stress_level, entry.journal_note or "", entry.sleep_hours,\
             s_score, s_label, now.strftime("%Y-%m-%d"), now.isoformat())\
        )\
        conn.commit()\
    finally:\
        conn.close()\
    return \{"message": "Mood logged successfully!"\}\
\
\
@app.get("/mood/history")\
def get_mood_history(authorization: str = Header(None), limit: int = 30):\
    username = get_current_user(authorization)\
    conn = get_connection()\
    try:\
        rows = conn.execute(\
            """SELECT id, mood_score, mood_label, energy_level, stress_level,\
                      journal_note, sentiment_score, sentiment_label, sleep_hours, date, created_at\
               FROM moods WHERE username = ? ORDER BY created_at DESC LIMIT ?""",\
            (username, limit)\
        ).fetchall()\
    finally:\
        conn.close()\
    return \{"moods": [dict(r) for r in rows]\}\
\
\
@app.get("/mood/stats")\
def get_mood_stats(authorization: str = Header(None)):\
    username = get_current_user(authorization)\
    conn = get_connection()\
    try:\
        rows = conn.execute(\
            """SELECT mood_score, stress_level, energy_level, sleep_hours, date\
               FROM moods WHERE username = ? ORDER BY created_at DESC LIMIT 7""",\
            (username,)\
        ).fetchall()\
    finally:\
        conn.close()\
    if not rows:\
        return \{"avg_mood": 0, "avg_stress": 0, "avg_energy": 0, "avg_sleep": 0,\
                "total_entries": 0, "weekly_mood": []\}\
    moods = [dict(r) for r in rows]\
    return \{\
        "avg_mood":   round(sum(m["mood_score"]   for m in moods) / len(moods), 1),\
        "avg_stress": round(sum(m["stress_level"] for m in moods) / len(moods), 1),\
        "avg_energy": round(sum(m["energy_level"] for m in moods) / len(moods), 1),\
        "avg_sleep":  round(sum(m["sleep_hours"]  for m in moods) / len(moods), 1),\
        "total_entries": len(moods),\
        "weekly_mood": list(reversed([\
            \{"date": m["date"], "mood_score": m["mood_score"],\
             "stress_level": m["stress_level"], "energy_level": m["energy_level"]\}\
            for m in moods\
        ])),\
    \}\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# DASHBOARD ROUTES  (/dashboard/summary  /dashboard/calendar)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
@app.get("/dashboard/summary")\
def get_dashboard_summary(authorization: str = Header(None)):\
    username = get_current_user(authorization)\
    conn = get_connection()\
    try:\
        rows = conn.execute(\
            """SELECT mood_score, stress_level, energy_level, sleep_hours,\
                      sentiment_score, journal_note, date, mood_label\
               FROM moods WHERE username = ? ORDER BY created_at DESC LIMIT 14""",\
            (username,)\
        ).fetchall()\
        latest_q = conn.execute(\
            """SELECT category, severity, score FROM questionnaires\
               WHERE username = ? ORDER BY created_at DESC LIMIT 1""",\
            (username,)\
        ).fetchone()\
    finally:\
        conn.close()\
\
    if not rows:\
        return \{"has_data": False, "wellness_tip": get_wellness_tip()\}\
\
    moods = [dict(r) for r in rows]\
    week = moods[:7]\
\
    mood_trend = list(reversed([\
        \{"date": m["date"], "mood_score": m["mood_score"],\
         "stress_level": m["stress_level"], "energy_level": m["energy_level"],\
         "sentiment_score": m["sentiment_score"]\}\
        for m in moods\
    ]))\
\
    mood_labels: dict = \{\}\
    for m in moods:\
        lbl = m.get("mood_label", "Unknown")\
        mood_labels[lbl] = mood_labels.get(lbl, 0) + 1\
\
    sentiment_trend = [\
        \{"date": m["date"], "sentiment": m["sentiment_score"]\}\
        for m in reversed(moods) if m.get("journal_note")\
    ]\
\
    return \{\
        "has_data":          True,\
        "total_entries":     len(moods),\
        "avg_mood":          round(sum(m["mood_score"]   for m in week) / len(week), 1),\
        "avg_stress":        round(sum(m["stress_level"] for m in week) / len(week), 1),\
        "avg_energy":        round(sum(m["energy_level"] for m in week) / len(week), 1),\
        "avg_sleep":         round(sum(m["sleep_hours"]  for m in week) / len(week), 1),\
        "mood_trend":        mood_trend,\
        "mood_distribution": mood_labels,\
        "sentiment_trend":   sentiment_trend,\
        "latest_assessment": dict(latest_q) if latest_q else None,\
        "wellness_tip":      get_wellness_tip(),\
    \}\
\
\
@app.get("/dashboard/calendar")\
def get_mood_calendar(authorization: str = Header(None)):\
    username = get_current_user(authorization)\
    conn = get_connection()\
    try:\
        rows = conn.execute(\
            """SELECT date, mood_score, mood_label FROM moods\
               WHERE username = ? ORDER BY created_at DESC LIMIT 60""",\
            (username,)\
        ).fetchall()\
    finally:\
        conn.close()\
    calendar_data: dict = \{\}\
    for r in rows:\
        if r["date"] not in calendar_data:\
            calendar_data[r["date"]] = \{"mood_score": r["mood_score"], "mood_label": r["mood_label"]\}\
    return \{"calendar": calendar_data\}\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# CHATBOT ROUTES  (/chatbot/send  /chatbot/history)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
OPENAI_BASE_URL = os.getenv("AI_INTEGRATIONS_OPENAI_BASE_URL", "")\
OPENAI_API_KEY  = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY",  "")\
\
SYSTEM_PROMPT = """You are MindBuddy, a warm and compassionate mental health support assistant\
for college students. Be warm, concise, and easy to understand. Never diagnose or prescribe\
medication. Recommend professional help when needed (iCall: 9152987821). Keep responses\
under 150 words. Use a friendly, conversational tone."""\
\
FALLBACK_RESPONSES = [\
    "I hear you. It sounds like you're going through a tough time. Remember, it's okay to not be okay sometimes. \uc0\u55357 \u56473 ",\
    "Thank you for sharing that with me. Taking small steps is still moving forward \'97 you've got this!",\
    "That sounds really difficult. Have you tried taking a few slow, deep breaths? It can help calm the mind.",\
    "You're not alone in feeling this way. Many students experience the same pressure. Be kind to yourself today. \uc0\u55356 \u57119 ",\
    "It's brave of you to talk about how you feel. Consider reaching out to a counsellor if things feel overwhelming.",\
    "Progress isn't always linear. It's okay to have bad days \'97 what matters is you keep going. \uc0\u55357 \u56908 ",\
    "Remember: you don't have to have everything figured out right now. One step at a time.",\
    "I'm here to listen. Talking about your feelings is already a huge step. I'm proud of you!",\
    "Feeling overwhelmed is normal, especially during exam season. Try breaking your day into small chunks.",\
    "Sometimes the bravest thing you can do is rest. Give yourself permission to take a break today.",\
]\
\
\
def get_ai_response(user_message: str, chat_history: list) -> str:\
    if not OPENAI_BASE_URL or not OPENAI_API_KEY:\
        return random.choice(FALLBACK_RESPONSES)\
    try:\
        from openai import OpenAI\
        client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)\
        messages = [\{"role": "system", "content": SYSTEM_PROMPT\}]\
        for chat in chat_history[-6:]:\
            messages.append(\{"role": "user",      "content": chat["user_message"]\})\
            messages.append(\{"role": "assistant", "content": chat["bot_reply"]\})\
        messages.append(\{"role": "user", "content": user_message\})\
        response = client.chat.completions.create(\
            model="gpt-4o-mini", messages=messages, max_tokens=200\
        )\
        reply = response.choices[0].message.content or ""\
        return reply.strip() or random.choice(FALLBACK_RESPONSES)\
    except Exception as e:\
        print(f"AI error: \{e\}")\
        return random.choice(FALLBACK_RESPONSES)\
\
\
@app.post("/chatbot/send")\
def send_message(msg: ChatMessage, authorization: str = Header(None)):\
    username = get_current_user(authorization)\
    conn = get_connection()\
    try:\
        recent = conn.execute(\
            """SELECT user_message, bot_reply FROM chats\
               WHERE username = ? ORDER BY created_at DESC LIMIT 6""",\
            (username,)\
        ).fetchall()\
        recent_chats = [dict(r) for r in reversed(recent)]\
        bot_reply = get_ai_response(msg.message, recent_chats)\
        timestamp = datetime.utcnow().isoformat()\
        conn.execute(\
            "INSERT INTO chats (username, user_message, bot_reply, created_at) VALUES (?, ?, ?, ?)",\
            (username, msg.message, bot_reply, timestamp)\
        )\
        conn.commit()\
    finally:\
        conn.close()\
    return \{"reply": bot_reply, "timestamp": timestamp\}\
\
\
@app.get("/chatbot/history")\
def get_chat_history(authorization: str = Header(None), limit: int = 20):\
    username = get_current_user(authorization)\
    conn = get_connection()\
    try:\
        rows = conn.execute(\
            """SELECT user_message, bot_reply, created_at FROM chats\
               WHERE username = ? ORDER BY created_at DESC LIMIT ?""",\
            (username, limit)\
        ).fetchall()\
    finally:\
        conn.close()\
    return \{"chats": list(reversed([dict(r) for r in rows]))\}\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# QUESTIONNAIRE ROUTES  (/questionnaire/questions/\{category\}  /questionnaire/submit)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
QUESTIONS = \{\
    "general": [\
        \{"id": "q1", "text": "How often do you feel overwhelmed?",\
         "options": ["Never", "Sometimes", "Often", "Always"], "weights": [0, 1, 2, 3]\},\
        \{"id": "q2", "text": "How would you rate your sleep quality?",\
         "options": ["Very Good", "Good", "Poor", "Very Poor"], "weights": [0, 1, 2, 3]\},\
        \{"id": "q3", "text": "Do you feel emotionally drained after daily tasks?",\
         "options": ["No", "Occasionally", "Frequently", "All the time"], "weights": [0, 1, 2, 3]\},\
        \{"id": "q4", "text": "How often do you feel hopeful about the future?",\
         "options": ["Always", "Often", "Rarely", "Never"], "weights": [0, 1, 2, 3]\},\
        \{"id": "q5", "text": "Can you concentrate on tasks for extended periods?",\
         "options": ["Yes easily", "With some effort", "With great difficulty", "Cannot concentrate"],\
         "weights": [0, 1, 2, 3]\},\
    ],\
    "stress": [\
        \{"id": "s1", "text": "How often do you feel under pressure to meet deadlines?",\
         "options": ["Rarely", "Sometimes", "Often", "Always"], "weights": [0, 1, 2, 3]\},\
        \{"id": "s2", "text": "Do you have difficulty relaxing after a stressful day?",\
         "options": ["No", "Occasionally", "Often", "Always"], "weights": [0, 1, 2, 3]\},\
        \{"id": "s3", "text": "Do you experience physical symptoms of stress (headaches, tension)?",\
         "options": ["Never", "Rarely", "Sometimes", "Frequently"], "weights": [0, 1, 2, 3]\},\
    ],\
    "anxiety": [\
        \{"id": "a1", "text": "How often do you feel nervous or on edge?",\
         "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],\
         "weights": [0, 1, 2, 3]\},\
        \{"id": "a2", "text": "Do you worry excessively about different things?",\
         "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"],\
         "weights": [0, 1, 2, 3]\},\
        \{"id": "a3", "text": "Do you feel afraid something terrible might happen?",\
         "options": ["Not at all", "Several days", "Often", "Nearly every day"],\
         "weights": [0, 1, 2, 3]\},\
    ],\
    "burnout": [\
        \{"id": "b1", "text": "Do you feel detached from your studies or work?",\
         "options": ["Not at all", "Sometimes", "Often", "Always"], "weights": [0, 1, 2, 3]\},\
        \{"id": "b2", "text": "Do you feel your efforts don't make a difference?",\
         "options": ["Rarely", "Sometimes", "Often", "Always"], "weights": [0, 1, 2, 3]\},\
        \{"id": "b3", "text": "Do you feel exhausted even before starting your day?",\
         "options": ["Never", "Rarely", "Often", "Every day"], "weights": [0, 1, 2, 3]\},\
    ],\
\}\
\
RECOMMENDATIONS = \{\
    "Low": [\
        "You seem to be managing well! Keep maintaining healthy habits.",\
        "Continue your regular exercise and sleep routines.",\
        "Consider journaling to preserve this positive state.",\
    ],\
    "Moderate": [\
        "Consider talking to a trusted friend or counsellor.",\
        "Practice mindfulness or meditation for 10 minutes daily.",\
        "Try to set clear boundaries between study/work and rest.",\
        "Limit caffeine and screen time before bed.",\
    ],\
    "High": [\
        "Please consider speaking to a mental health professional.",\
        "Reach out to your college counselling service.",\
        "Contact iCall helpline: 9152987821",\
        "Break tasks into very small steps and celebrate small wins.",\
        "Prioritise rest \'97 your wellbeing matters more than grades.",\
    ],\
\}\
\
\
@app.get("/questionnaire/questions/\{category\}")\
def get_questions(category: str):\
    if category not in QUESTIONS:\
        raise HTTPException(status_code=404, detail=f"Category '\{category\}' not found.")\
    return \{"category": category, "questions": QUESTIONS[category]\}\
\
\
@app.post("/questionnaire/submit")\
def submit_questionnaire(data: QuestionnaireAnswer, authorization: str = Header(None)):\
    username = get_current_user(authorization)\
    if data.category not in QUESTIONS:\
        raise HTTPException(status_code=400, detail="Invalid category.")\
\
    questions = QUESTIONS[data.category]\
    total_score = 0\
    for q in questions:\
        qid = q["id"]\
        if qid in data.answers:\
            idx = data.answers[qid]\
            if 0 <= idx < len(q["weights"]):\
                total_score += q["weights"][idx]\
\
    max_score  = len(questions) * 3\
    pct        = (total_score / max_score * 100) if max_score else 0\
    severity   = "Low" if pct <= 30 else ("Moderate" if pct <= 65 else "High")\
    follow_up  = (["stress", "anxiety", "burnout"]\
                  if data.category == "general" and pct > 40 else [])\
\
    conn = get_connection()\
    try:\
        conn.execute(\
            """INSERT INTO questionnaires\
               (username, category, score, max_score, severity, answers_json, created_at)\
               VALUES (?, ?, ?, ?, ?, ?, ?)""",\
            (username, data.category, total_score, max_score, severity,\
             json.dumps(data.answers), datetime.utcnow().isoformat())\
        )\
        conn.commit()\
    finally:\
        conn.close()\
\
    return \{\
        "category":             data.category,\
        "score":                total_score,\
        "max_score":            max_score,\
        "severity":             severity,\
        "recommendations":      RECOMMENDATIONS[severity],\
        "follow_up_categories": follow_up,\
    \}\
\
\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
# WELLNESS ROUTES  (/wellness/tip  /wellness/emergency  /wellness/study-stress)\
# \uc0\u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \u9552 \
\
@app.get("/wellness/tip")\
def daily_tip():\
    return \{"tip": get_wellness_tip()\}\
\
\
@app.get("/wellness/emergency")\
def emergency_resources():\
    return \{\
        "resources": [\
            \{"name": "iCall (India)",         "number": "9152987821",    "description": "Free psychosocial support helpline by TISS",   "hours": "Mon\'96Sat, 8am\'9610pm"\},\
            \{"name": "Vandrevala Foundation", "number": "1860-2662-345", "description": "24/7 mental health helpline",                  "hours": "24 hours"\},\
            \{"name": "NIMHANS",               "number": "080-46110007",  "description": "National Institute of Mental Health helpline", "hours": "24 hours"\},\
            \{"name": "iCall WhatsApp",        "number": "+919152987821", "description": "WhatsApp support by iCall",                   "hours": "Mon\'96Sat, 8am\'9610pm"\},\
            \{"name": "Snehi",                 "number": "044-24640050",  "description": "Emotional support and suicide prevention",    "hours": "24 hours"\},\
        ],\
        "message": "You are not alone. Reaching out for help is a sign of strength. \uc0\u55357 \u56473 ",\
    \}\
\
\
@app.post("/wellness/study-stress")\
def log_study_stress(entry: StudyStressEntry, authorization: str = Header(None)):\
    username = get_current_user(authorization)\
\
    stress_score = 0\
    stress_score += min(entry.exams_this_week * 2, 6)\
    stress_score += min(entry.assignments_pending, 4)\
    stress_score += max(0, int((6 - entry.sleep_hours) * 1.5))\
    stress_score += min(int(entry.study_hours_per_day / 2), 3)\
    stress_score += 3 if entry.feeling_overwhelmed else 0\
\
    if stress_score <= 5:\
        level = "Low"\
        advice = [\
            "Your study load seems manageable. Keep your routine going!",\
            "Remember to take short breaks every 45-50 minutes.",\
        ]\
    elif stress_score <= 10:\
        level = "Moderate"\
        advice = [\
            "Prioritise your most urgent tasks first.",\
            "Try the Pomodoro technique \'97 25 minutes study, 5 minutes break.",\
            "Make sure you're getting at least 6\'967 hours of sleep.",\
        ]\
    else:\
        level = "High"\
        advice = [\
            "Your study load is very high. Break tasks into smaller chunks.",\
            "Talk to your professor if deadlines feel impossible.",\
            "Sleep is more important than cramming \'97 a rested brain learns faster.",\
            "Ask a classmate for help \'97 collaboration is not cheating!",\
        ]\
\
    conn = get_connection()\
    try:\
        conn.execute(\
            """INSERT INTO moods\
               (username, mood_score, mood_label, energy_level, stress_level,\
                journal_note, sleep_hours, sentiment_score, sentiment_label, date, created_at)\
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",\
            (username, 5, "Study Check-in", 5, stress_score,\
             entry.notes or f"Exams: \{entry.exams_this_week\}, Assignments: \{entry.assignments_pending\}",\
             entry.sleep_hours, 0.0, "Neutral",\
             datetime.utcnow().strftime("%Y-%m-%d"), datetime.utcnow().isoformat())\
        )\
        conn.commit()\
    finally:\
        conn.close()\
\
    return \{"stress_level": level, "stress_score": stress_score, "advice": advice\}}