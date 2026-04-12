import streamlit as st
from groq import Groq
import time, json, re, logging
from datetime import datetime
from pathlib import Path

# 1. LOGGING & CONFIG
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_DIR/"app.log", level=logging.ERROR)

st.set_page_config(page_title="AI Python Mentor PRO", layout="wide")

# 2. SESSION STATE (Xatolikni oldini olish uchun barcha o'zgaruvchilarni init qilamiz)
if "request_history" not in st.session_state:
    st.session_state.request_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username" not in st.session_state:
    st.session_state.username = None

# 3. RATE LIMITER (Xatosiz versiya)
def check_rate_limit():
    now = datetime.now()
    # Faqat oxirgi 60 soniyadagi so'rovlarni saqlaymiz
    st.session_state.request_history = [t for t in st.session_state.request_history 
                                        if (now - t).total_seconds() < 60]
    if len(st.session_state.request_history) >= 10:
        return False
    st.session_state.request_history.append(now)
    return True

# 4. KOD MURAKKABLIGI
def get_complexity(code):
    points = len(re.findall(r'\b(if|for|while|elif|def|class|with)\b', code))
    if points <= 2: return "🟢 Sodda", "#3fb950"
    if points <= 6: return "🟡 O'rta", "#f0883e"
    return "🔴 Murakkab", "#f85149"

# --- UI QISMI ---
if not st.session_state.username:
    st.title("🐍 AI Python Mentor")
    user_input = st.text_input("Ismingiz:")
    if st.button("Kirish") and user_input:
        st.session_state.username = user_input
        st.rerun()
    st.stop()

# TABS
tabs = st.tabs(["💬 Chat", "🖥️ Runner", "📊 Dashboard"])

# TAB 1: CHAT
with tabs[0]:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Savol bering..."):
        if not check_rate_limit():
            st.error("🛑 Sekinroq! Minutiga 10 ta so'rov limiti bor.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            # Bu yerda Groq API chaqiruvi bo'ladi...
            st.success("Xabar yuborildi!")

# TAB 2: RUNNER
with tabs[1]:
    code_input = st.text_area("Python kodi:", height=150)
    if code_input:
        lbl, clr = get_complexity(code_input)
        st.markdown(f"Murakkablik: <b style='color:{clr}'>{lbl}</b>", unsafe_allow_html=True)

# TAB 3: DASHBOARD (Rasmda xato bergan joy shu yer)
with tabs[2]:
    st.subheader("📊 Tizim statistikasi")
    col_a, col_b = st.columns(2)
    
    # .get() ishlatish xavfsizroq yoki default qiymat berish kerak
    history = st.session_state.get("request_history", [])
    msgs = st.session_state.get("messages", [])
    
    col_a.metric("So'rovlar (so'nggi 1 min)", len(history))
    col_b.metric("Suhbatlar soni", len(msgs))
