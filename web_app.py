import streamlit as st
import re, logging
from datetime import datetime
from pathlib import Path

# 1. INITIAL SETUP (Eng tepada bo'lishi shart)
st.set_page_config(page_title="AI Python Mentor PRO", layout="wide")

# 2. XAVFSIZ SESSION STATE (Barcha tablar uchun o'zgaruvchilar)
state_keys = {
    "username": None,
    "messages": [],
    "request_history": [],
    "quiz_score": 0,
    "current_tab": "Chat"
}

for key, value in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 3. RATE LIMITER FUNKSIYASI
def check_rate_limit():
    now = datetime.now()
    # Request history mavjudligini qayta tekshirish
    history = st.session_state.get("request_history", [])
    # Oxirgi 60 soniyadagi so'rovlarni filtrlash
    valid_history = [t for t in history if (now - t).total_seconds() < 60]
    st.session_state.request_history = valid_history
    
    if len(valid_history) >= 10:
        return False
    
    st.session_state.request_history.append(now)
    return True

# --- LOGIN QISMI ---
if st.session_state.username is None:
    st.title("🐍 AI Python Mentor PRO")
    user_input = st.text_input("Ismingizni kiriting:")
    if st.button("Kirish"):
        if user_input:
            st.session_state.username = user_input
            st.rerun()
    st.stop()

# --- ASOSIY INTERFEYS ---
st.title(f"Xush kelibsiz, {st.session_state.username}! 🚀")

# 12 ta tabni yaratish
tabs = st.tabs([
    "💬 Chat", "🤖 Copilot", "🖥️ Runner", "🏆 Quiz", 
    "🌐 Tarjima", "✂️ Snippets", "📈 Progress", "⚖️ Multi-Model", 
    "🔗 Share", "🐙 GitHub", "🗓️ Challenge", "📊 Dashboard"
])

# 1. CHAT TAB
with tabs[0]:
    st.caption("Maslahat: Ctrl + Enter orqali yuboring.")
    # Xabarlarni xavfsiz chiqarish
    msgs = st.session_state.get("messages", [])
    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Savol bering..."):
        if not check_rate_limit():
            st.error("🛑 Sekinroq! Limit: 1 minutda 10 ta so'rov.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            # Bu yerda API chaqiruvi bo'ladi
            st.info("AI javob bermoqda...")

# 3. RUNNER TAB (Complexity bilan)
with tabs[2]:
    code = st.text_area("Python kodi:", height=150, key="runner_area")
    if code:
        points = len(re.findall(r'\b(if|for|while|def|class)\b', code))
        status = "🟢 Sodda" if points < 3 else "🟡 O'rta" if points < 7 else "🔴 Murakkab"
        st.write(f"Kod murakkabligi: {status}")

# 12. DASHBOARD TAB (Xatolik bergan joyni himoyaladik)
with tabs[11]:
    st.subheader("📊 Tizim holati")
    c1, c2 = st.columns(2)
    
    # Xavfsiz o'qish: .get() va len()
    req_count = len(st.session_state.get("request_history", []))
    msg_count = len(st.session_state.get("messages", []))
    
    c1.metric("So'rovlar (1 min)", req_count)
    c2.metric("Jami xabarlar", msg_count)
    
    if st.button("Tarixni tozalash"):
        st.session_state.messages = []
        st.rerun()
