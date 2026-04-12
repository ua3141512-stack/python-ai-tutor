import streamlit as st
from groq import Groq
import time, json, shelve, hashlib, requests, difflib, os, logging, re
from datetime import datetime, date
from pathlib import Path
import pandas as pd

# ─────────────────────────────────────
# 1. LOGGING & PATHS (🔴 Kritik)
# ─────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "mentor_pro.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH  = str(DATA_DIR / "users_v5")

# ─────────────────────────────────────
# 2. PAGE CONFIG & UI THEME
# ─────────────────────────────────────
st.set_page_config(page_title="AI Python Mentor PRO v5.1", layout="wide", page_icon="🐍")

# JavaScript: Keyboard Shortcuts (Ctrl+Enter)
st.markdown("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const buttons = doc.querySelectorAll('button');
        const submitBtn = Array.from(buttons).find(el => 
            el.innerText.includes('Yuborish') || el.innerText.includes('Bajarish') || el.innerText.includes('Saqlash')
        );
        if (submitBtn) submitBtn.click();
    }
});
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# 3. CORE LOGIC (Rate Limit & Complexity)
# ─────────────────────────────────────
def is_rate_limited():
    """Minutiga 10 ta so'rov chegarasi (🔴 Production)"""
    now = datetime.now()
    if "request_history" not in st.session_state:
        st.session_state.request_history = []
    st.session_state.request_history = [t for t in st.session_state.request_history if (now - t).total_seconds() < 60]
    if len(st.session_state.request_history) >= 10:
        return True
    st.session_state.request_history.append(now)
    return False

def get_complexity(code):
    """Cyclomatic Complexity simulyatsiyasi (🟢 Researcher tool)"""
    points = len(re.findall(r'\b(if|for|while|elif|except|with|and|or)\b', code))
    if points <= 2: return "🟢 Juda sodda", "#3fb950"
    if points <= 5: return "🟡 O'rta", "#f0883e"
    return "🔴 Murakkab (Refaktor kerak)", "#f85149"

# ─────────────────────────────────────
# 4. DATABASE & SESSION STATE
# ─────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("GROQ_API_KEY")
    return Groq(api_key=key) if key else None

client = get_client()

DEFAULTS = {
    "username": None, "messages": [], "total_tokens": 0, "theme": "dark",
    "quiz_score": 0, "quiz_total": 0, "snippets": [], "shared_codes": {},
    "dashboard_api_calls": [], "progress_topics": {}
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ─────────────────────────────────────
# 5. MENTOR PROMPTS
# ─────────────────────────────────────
MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
MENTOR_MODES = {
    "Python Mentor 🐍": "Sen professional Python arxitektisan. Kodni PEP8 va SOLID bo'yicha tahlil qilasan.",
    "Debug Ustasi 🐛": "Sen xatolarni topish bo'yicha ekspertisan. Fokus: Logic errors & Tracebacks.",
    "Algoritm Muallimi 📚": "Fokus: DSA va Complexity Analysis."
}

# ─────────────────────────────────────
# MAIN APP INTERFACE
# ─────────────────────────────────────
if not st.session_state.username:
    st.title("🐍 AI Python Mentor PRO")
    name = st.text_input("Ismingiz:")
    if st.button("Kirish"):
        if name: 
            st.session_state.username = name
            st.rerun()
    st.stop()

# Header
c1, c2 = st.columns([4, 1])
c1.title(f"Xush kelibsiz, {st.session_state.username}! 🚀")
if c2.button("🚪 Chiqish"):
    st.session_state.username = None
    st.rerun()

# Tabs
tabs = st.tabs([
    "💬 Chat", "🤖 Copilot", "🖥️ Runner", "🏆 Quiz", 
    "🌐 Tarjima", "✂️ Snippets", "📈 Progress", "⚖️ Multi-Model", 
    "🔗 Share", "🐙 GitHub", "🗓️ Challenge", "📊 Dashboard"
])

# ─────────────────────────────────────
# TAB 1: CHAT
# ─────────────────────────────────────
with tabs[0]:
    st.caption("Maslahat: Ctrl + Enter orqali tezkor yuboring.")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Savol bering..."):
        if is_rate_limited():
            st.error("🛑 Sekinroq! Minutiga faqat 10 ta so'rov mumkin.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            try:
                resp = client.chat.completions.create(
                    model=MODELS[0],
                    messages=[{"role": "user", "content": prompt}]
                ).choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": resp})
                with st.chat_message("assistant"): st.markdown(resp)
            except Exception as e:
                logging.error(f"Chat Error: {e}")
                st.error("Xatolik yuz berdi. Log saqlandi.")

# ─────────────────────────────────────
# TAB 3: RUNNER & COMPLEXITY (🟢 Yangi)
# ─────────────────────────────────────
with tabs[2]:
    st.header("🖥️ Python Code Runner")
    code = st.text_area("Kodingizni yozing:", height=250, placeholder="print('Hello World')")
    
    if code:
        lbl, clr = get_complexity(code)
        st.markdown(f"**Murakkablik tahlili:** <span style='color:{clr}'>{lbl}</span>", unsafe_allow_html=True)

    if st.button("▶️ Bajarish"):
        # Piston API integratsiyasi simulyatsiyasi (oldingi kodingizdagi run_piston funksiyasi)
        st.info("Kod serverga yuborildi...")

# ─────────────────────────────────────
# TAB 12: DASHBOARD & LOGS (🔴 Yangi)
# ─────────────────────────────────────
with tabs[11]:
    st.header("📊 Tizim Holati")
    col_a, col_b = st.columns(2)
    col_a.metric("Jami so'rovlar", len(st.session_state.request_history))
    col_b.metric("Xabarlar soni", len(st.session_state.messages))

    if st.checkbox("Xatolar logini ko'rish (🔴 Error Logging)"):
        if LOG_DIR.joinpath("mentor_pro.log").exists():
            with open(LOG_DIR / "mentor_pro.log", "r") as f:
                st.code(f.read()[-1000:], language="text")
        else:
            st.write("Hozircha xatolar yo'q.")

# (Qolgan 9 ta tab ham shu strukturada davom etadi...)
