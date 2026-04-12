"""
AI Python Mentor LMS v6.0 (PRO)
Muallif: Jaloliddin | LMS Integrated Version
"""

import streamlit as st
from groq import Groq
import time, json, shelve, hashlib, requests, difflib, sqlite3, os
from datetime import datetime, date
from pathlib import Path
import pandas as pd

# ─────────────────────────────────────
# PATHS & DB INITIALIZATION
# ─────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = str(DATA_DIR / "users_v6")

def init_global_db():
    conn = sqlite3.connect(str(DATA_DIR / "mentor_lms.db"), check_same_thread=False)
    c = conn.cursor()
    # Studentlar progressini markaziy saqlash
    c.execute('''CREATE TABLE IF NOT EXISTS global_progress 
                 (username TEXT, topic TEXT, score INTEGER, date TEXT)''')
    # O'qituvchi topshiriqlari
    c.execute('''CREATE TABLE IF NOT EXISTS assignments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, desc TEXT, deadline TEXT, created_by TEXT)''')
    # Studentlar javoblari
    c.execute('''CREATE TABLE IF NOT EXISTS submissions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, student TEXT, 
                  code TEXT, grade TEXT, feedback TEXT, status TEXT)''')
    conn.commit()
    return conn

global_conn = init_global_db()

# ─────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────
st.set_page_config(page_title="Mentor LMS PRO", layout="wide", page_icon="🐍")

# ─────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────
if "username" not in st.session_state: st.session_state.username = None
if "role" not in st.session_state: st.session_state.role = "Student"
if "messages" not in st.session_state: st.session_state.messages = []
if "theme" not in st.session_state: st.session_state.theme = "dark"
# (Boshqa v5.0 session state lari ham shu yerda...)

# ─────────────────────────────────────
# LOGIN TIZIMI (Rollari bilan)
# ─────────────────────────────────────
if not st.session_state.username:
    st.markdown("<h1 style='text-align:center;'>🐍 AI Python Mentor LMS</h1>", unsafe_allow_html=True)
    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        with st.form("login_form"):
            uname = st.text_input("👤 Ismingiz:")
            urole = st.selectbox("Siz kimsiz?", ["Student", "Teacher"])
            submit = st.form_submit_button("🚀 Kirish")
            if submit and uname:
                st.session_state.username = uname.strip()
                st.session_state.role = urole
                st.rerun()
    st.stop()

# ─────────────────────────────────────
# MENTOR PROMPTS & MODELS (v5.0 dagi kabi)
# ─────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

# ─────────────────────────────────────
# TABS (Dinamik: Teacher uchun qo'shimcha tab)
# ─────────────────────────────────────
TABS = ["💬 Chat", "🤖 Copilot", "🖥️ Runner", "🏆 Quiz", "🗓️ Challenge", "📈 Progress", "📊 Dashboard"]
if st.session_state.role == "Teacher":
    TABS.insert(0, "👨‍🏫 Teacher Panel")

current_tabs = st.tabs(TABS)

# ─────────────────────────────────────
# TAB: TEACHER PANEL (Faqat o'qituvchi uchun)
# ─────────────────────────────────────
if st.session_state.role == "Teacher":
    with current_tabs[0]:
        st.header("👨‍🏫 O'qituvchi Boshqaruv Paneli")
        t1, t2, t3 = st.tabs(["📊 Studentlar Progressi", "📝 Vazifa Berish", "📥 Kelgan Vazifalar"])
        
        with t1:
            st.subheader("Barcha studentlar statistikasi")
            df_prog = pd.read_sql_query("SELECT * FROM global_progress", global_conn)
            if not df_prog.empty:
                pivot = df_prog.pivot_table(index='username', columns='topic', values='score', aggfunc='sum').fillna(0)
                st.dataframe(pivot, use_container_width=True)
                st.bar_chart(pivot)
            else:
                st.info("Hozircha hech qanday progress mavjud emas.")

        with t2:
            st.subheader("Yangi topshiriq yaratish")
            with st.form("task_form"):
                title = st.text_input("Vazifa nomi")
                desc = st.text_area("Vazifa sharti (kod yozish yoki savol)")
                dl = st.date_input("Deadline")
                if st.form_submit_button("E'lon qilish"):
                    c = global_conn.cursor()
                    c.execute("INSERT INTO assignments (title, desc, deadline, created_by) VALUES (?,?,?,?)",
                              (title, desc, str(dl), st.session_state.username))
                    global_conn.commit()
                    st.success("✅ Vazifa barcha studentlarga yuborildi!")

        with t3:
            st.subheader("Tekshirilmagan ishlar")
            subs = pd.read_sql_query("SELECT * FROM submissions WHERE status IS NULL", global_conn)
            if not subs.empty:
                for i, row in subs.iterrows():
                    with st.expander(f"Student: {row['student']} | Task ID: {row['task_id']}"):
                        st.code(row['code'], language="python")
                        grade = st.slider("Baho (0-100)", 0, 100, 80, key=f"g_{i}")
                        feedback = st.text_input("Izoh", key=f"f_{i}")
                        if st.button("Baholash", key=f"b_{i}"):
                            c = global_conn.cursor()
                            c.execute("UPDATE submissions SET grade=?, feedback=?, status='graded' WHERE id=?",
                                      (grade, feedback, row['id']))
                            global_conn.commit()
                            st.rerun()
            else:
                st.info("Yangi kelib tushgan ishlar yo'q.")

# ─────────────────────────────────────
# TAB: CHAT & QUIZ (Student progressini bazaga yozish qismi)
# ─────────────────────────────────────
# (Bu yerda v5.0 dagi Chat, Runner, Copilot kodlari bo'ladi)
# MUHIM: Quiz to'g'ri bo'lganda global bazaga ham yozamiz:

def save_global_score(topic, score):
    c = global_conn.cursor()
    c.execute("INSERT INTO global_progress VALUES (?,?,?,?)",
              (st.session_state.username, topic, score, str(date.today())))
    global_conn.commit()

# ... (v5.0 Quiz kodi ichida save_global_score chaqiriladi)

# ─────────────────────────────────────
# STUDENT UCHUN VAZIFALAR (Progress tabida ko'rsatish mumkin)
# ─────────────────────────────────────
with (current_tabs[1] if st.session_state.role == "Teacher" else current_tabs[5]):
    if st.session_state.role == "Student":
        st.subheader("📝 O'qituvchi bergan vazifalar")
        tasks = pd.read_sql_query("SELECT * FROM assignments", global_conn)
        for _, t in tasks.iterrows():
            with st.expander(f"📌 {t['title']} (Deadline: {t['deadline']})"):
                st.write(t['desc'])
                ans_code = st.text_area("Yechimni yozing:", key=f"ans_{t['id']}")
                if st.button("Topshirish", key=f"sub_{t['id']}"):
                    c = global_conn.cursor()
                    c.execute("INSERT INTO submissions (task_id, student, code) VALUES (?,?,?)",
                              (t['id'], st.session_state.username, ans_code))
                    global_conn.commit()
                    st.success("Vazifa yuborildi! O'qituvchi tekshiruvini kuting.")

# ─────────────────────────────────────
# SIDEBAR & FOOTER
# ─────────────────────────────────────
with st.sidebar:
    st.write(f"👤 Foydalanuvchi: **{st.session_state.username}**")
    st.write(f"🎭 Rol: **{st.session_state.role}**")
    if st.button("Chiqish"):
        st.session_state.username = None
        st.rerun()
