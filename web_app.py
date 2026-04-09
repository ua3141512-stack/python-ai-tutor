"""
AI Python Mentor + Copilot - Professional Streamlit Application
Muallif: Jaloliddin | Magistr/Researcher
Versiya: 3.0.0 (Copilot qo'shildi)
"""

import streamlit as st
from groq import Groq
import time
import json
from datetime import datetime

# ============================================================
# 1. SAHIFA SOZLAMALARI
# ============================================================
st.set_page_config(
    page_title="AI Python Mentor",
    layout="wide",
    page_icon="🐍",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI Python Mentor v3.0 | Jaloliddin | Copilot qo'shildi"}
)

# ============================================================
# 2. GROQ CLIENT
# ============================================================
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        return None, None
    try:
        return Groq(api_key=api_key), api_key
    except Exception as e:
        st.error(f"Client xatolik: {e}")
        return None, None

client, api_key = get_groq_client()

# ============================================================
# 3. CSS DIZAYN
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #1c2128;
    --accent-green: #00d4aa;
    --accent-blue: #4f9cf9;
    --accent-purple: #bc8cff;
    --accent-orange: #f0883e;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --border-color: #30363d;
}

.stApp { background-color: var(--bg-primary) !important; font-family: 'Inter', sans-serif; }

h1 {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

/* Tablar */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border-color) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 8px 24px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue)) !important;
    color: #000 !important;
    font-weight: 700 !important;
}

/* Chat */
.stChatMessage {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatMessageContent"] {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}
.stChatInputContainer {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}
.stChatInputContainer textarea { color: var(--text-primary) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Metrika */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

/* Tugmalar */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue)) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,212,170,0.3) !important;
}

/* Kod */
code {
    background: var(--bg-card) !important;
    color: var(--accent-green) !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
}
pre {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

/* TextArea (Copilot uchun) */
.stTextArea textarea {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}

/* Radio */
.stRadio > div { gap: 8px !important; }
.stRadio label {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}

/* Copilot natija kutucha */
.copilot-suggestion {
    background: rgba(79, 156, 249, 0.06);
    border: 1px solid rgba(79, 156, 249, 0.2);
    border-left: 3px solid var(--accent-blue);
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 8px;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    line-height: 1.7;
}

/* Badge */
.copilot-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(188,140,255,0.1); border: 1px solid rgba(188,140,255,0.3);
    border-radius: 20px; padding: 2px 10px; font-size: 11px;
    color: var(--accent-purple); font-weight: 700; letter-spacing: 0.5px;
}
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3);
    border-radius: 20px; padding: 4px 12px; font-size: 12px;
    color: #3fb950; font-weight: 500;
}
.status-dot {
    width: 6px; height: 6px; background: #3fb950;
    border-radius: 50%; animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

hr { border-color: var(--border-color) !important; margin: 16px 0 !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. SESSION STATE
# ============================================================
def init_session_state():
    defaults = {
        "messages": [],
        "total_tokens_used": 0,
        "session_start": datetime.now().strftime("%H:%M"),
        "conversation_count": 0,
        "error_count": 0,
        "copilot_result": "",
        "copilot_action_used": "",
        "quick_prompt": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ============================================================
# 5. SYSTEM PROMPTS
# ============================================================
SYSTEM_PROMPTS = {
    "Python Mentor 🐍": """Sen magistr darajasidagi tajribali Python arxitektisan va mentorsan.
ASOSIY VAZIFALAR:
1. Kod tahlili: Time/Space complexity (Big-O), PEP8, SOLID prinsiplari
2. Xavfsizlik: SQL injection, XSS, input validation zaifliklarini topish
3. Optimizatsiya: Memory leak, bottleneck, anti-pattern larni aniqlash
4. Best practices: Design pattern tavsiyalari, clean code
5. Debug: Error xabarlarini tushuntirish va yechim taklif qilish
Javoblaring aniq, lo'nda, kod namunali va O'zbek tilida bo'lsin.""",

    "Code Reviewer 🔍": """Sen yuqori malakali Code Review mutaxassisisan.
Har bir kod uchun:
## 📊 Umumiy Baho: X/10
## ✅ Yaxshi tomonlar:
## ⚠️ Kamchiliklar:
## 🔧 Yaxshilangan kod:
```python
# ...
```
## 📈 Complexity: Time O(?) | Space O(?)
Faqat O'zbek tilida yozish.""",

    "Debug Ustasi 🐛": """Sen Python debug ekspertisan.
Har xato uchun: 🔍 Sabab → 📍 Joyi → 🔧 Yechim → 💡 Oldini olish → ✅ Tuzatilgan kod.
Faqat O'zbek tilida yozish.""",

    "Algoritm Muallimi 📚": """Sen DSA bo'yicha professor darajasidagi o'qituvchisan.
Tushuntirishda: Nazariya → Vizual (ASCII) → Python kod → Complexity → Mashq savollari.
Faqat O'zbek tilida yozish.""",
}

COPILOT_SYSTEM = """Sen GitHub Copilot kabi AI kod yordamchisisan.
Foydalanuvchi yozayotgan yoki tugallanmagan Python kodini ko'rib, davom ettir yoki yaxshila.
QOIDALAR:
- FAQAT Python kodi qaytargin — hech qanday tushuntirish yo'q
- Tugallanmagan kod bo'lsa mantiqiy davom ettir
- To'liq kod bo'lsa optimallashtirilgan versiyasini ber
- Type hints qo'sh (agar yo'q bo'lsa)
- Docstring qo'sh
- PEP8 ga rioya qil
- Hech qanday markdown ``` belgisi qo'shma — sof Python kod yoz"""

COPILOT_EXPLAIN_SYSTEM = """Sen Python kod tushuntiruvchisisan.
Berilgan kodni O'zbek tilida, bosqichma-bosqich, juda aniq va tushunarli tushuntir.
Har muhim qatorni alohida izohlash bilan. Oxirida Time/Space complexity qo'sh."""

COPILOT_FIX_SYSTEM = """Sen Python xato tuzatuvchisisan.
Berilgan kodda barcha xatolarni (sintaksis, mantiq, runtime) top va tuzat.
Avval tuzatilgan kodni yoz, keyin O'zbek tilida qisqacha nimani o'zgartirganingni yoz."""

COPILOT_TEST_SYSTEM = """Sen Python test mutaxassisisan.
Berilgan kod uchun pytest bilan to'liq unit testlar yoz.
Normal holatlar, edge caseslar va xato holatlarini ham qamrab ol.
Oxirida O'zbek tilida testlar haqida qisqa izoh yoz."""

# ============================================================
# 6. YORDAMCHI FUNKSIYALAR
# ============================================================
def count_tokens_estimate(text: str) -> int:
    return len(text) // 4

def contains_code(text: str) -> bool:
    return any(k in text for k in ["```", "def ", "import ", "class ", "for ", "while "])

def format_message_time() -> str:
    return datetime.now().strftime("%H:%M")

def export_chat_history() -> str:
    return json.dumps({
        "export_time": datetime.now().isoformat(),
        "session_start": st.session_state.session_start,
        "total_messages": len(st.session_state.messages),
        "messages": st.session_state.messages
    }, ensure_ascii=False, indent=2)

def get_ai_response(client, messages, system_prompt, model, temperature, max_tokens, streaming):
    """API ga faqat role+content yuborish — time/model maydonlari chiqariladi."""
    clean = [{"role": m["role"], "content": m["content"]} for m in messages]
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}] + clean,
        stream=streaming,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
    )

def copilot_call(client, code: str, system: str, model: str) -> str:
    """Copilot uchun oddiy API chaqiruvi — past temperature = deterministik kod."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": code}
        ],
        stream=False,
        temperature=0.15,
        max_tokens=2048,
    )
    return resp.choices[0].message.content

# ============================================================
# 7. SARLAVHA
# ============================================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title("🐍 AI Python Mentor + Copilot")
    st.caption("Magistratura darajasidagi intellektual dasturlash yordamchisi")
with col_status:
    if api_key:
        st.markdown('<div class="status-badge"><span class="status-dot"></span> Online</div>',
                    unsafe_allow_html=True)
    else:
        st.error("⚠️ Offline")

st.divider()

# ============================================================
# 8. SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Sozlamalar")

    mentor_mode = st.selectbox("🎯 Mentor rejimi", list(SYSTEM_PROMPTS.keys()))
    st.divider()

    model_choice = st.selectbox("🤖 AI Model", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ])

    temperature = st.slider("🌡️ Ijodkorlik", 0.0, 1.0, 0.7, 0.1,
                            help="Past=aniq/texnik | Yuqori=ijodiy")
    max_tokens = st.select_slider("📏 Javob uzunligi",
                                  options=[512, 1024, 2048, 4096, 8192], value=2048)
    max_history = st.slider("💬 Tariх uzunligi", 2, 30, 10, 2)
    use_streaming = st.toggle("⚡ Streaming", value=True)

    st.divider()
    st.markdown("### 📊 Statistika")
    c1, c2 = st.columns(2)
    c1.metric("💬 Xabarlar", len(st.session_state.messages))
    c2.metric("🔄 Suhbatlar", st.session_state.conversation_count)
    st.metric("🪙 Tokenlar", f"~{st.session_state.total_tokens_used:,}")
    st.metric("⏰ Boshlandi", st.session_state.session_start)

    st.divider()
    st.markdown("### 🛠️ Amallar")

    if st.button("🗑️ Suhbatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens_used = 0
        st.session_state.conversation_count = 0
        st.session_state.copilot_result = ""
        st.success("✅ Tozalandi!")
        time.sleep(0.4)
        st.rerun()

    if st.session_state.messages:
        st.download_button(
            "📥 Tarixni saqlash (JSON)", export_chat_history(),
            f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "application/json", use_container_width=True
        )

    st.divider()
    st.markdown("### 💡 Tezkor savollar")
    for q in ["Python list vs tuple?", "GIL nima?",
               "Decorator qanday ishlaydi?", "async/await tushuntir",
               "@staticmethod vs @classmethod"]:
        if st.button(q, use_container_width=True, key=f"q_{q}"):
            st.session_state.quick_prompt = q
            st.rerun()

    st.divider()
    st.markdown(
        '<p style="color:#8b949e;font-size:11px;text-align:center">'
        '🐍 v3.0 | Jaloliddin<br>Magistr/Researcher</p>',
        unsafe_allow_html=True
    )

# ============================================================
# 9. API KALIT TEKSHIRUVI
# ============================================================
if not api_key:
    st.warning("⚠️ `GROQ_API_KEY` ni Streamlit Secrets ga qo'shing.")
    st.code('# .streamlit/secrets.toml\nGROQ_API_KEY = "gsk_your_key_here"', language="toml")
    st.info("🔑 Bepul kalit: https://console.groq.com")
    st.stop()

# ============================================================
# 10. ASOSIY TABLAR
# ============================================================
tab_chat, tab_copilot = st.tabs(["💬  Chat Mentor", "🤖  AI Copilot"])

# ============================================================
# TAB 1 — CHAT MENTOR
# ============================================================
with tab_chat:

    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#8b949e;">
            <h2 style="color:#e6edf3;font-size:22px;">Salom! Men sizning AI Python Mentoringizman 👋</h2>
            <p style="font-size:14px;max-width:560px;margin:0 auto;">
                Python haqida istalgan savol bering, kodingizni tahlil qildiring yoki
                algoritmlar haqida bilib oling. Yoki <strong>AI Copilot</strong> tabiga o'ting!
            </p>
            <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:20px;">
                <span style="background:#1c2128;border:1px solid #30363d;border-radius:8px;padding:7px 14px;font-size:12px;">🔍 Kod tahlili</span>
                <span style="background:#1c2128;border:1px solid #30363d;border-radius:8px;padding:7px 14px;font-size:12px;">🐛 Debug yordam</span>
                <span style="background:#1c2128;border:1px solid #30363d;border-radius:8px;padding:7px 14px;font-size:12px;">📚 Algoritm ta'lim</span>
                <span style="background:#1c2128;border:1px solid #30363d;border-radius:8px;padding:7px 14px;font-size:12px;">⚡ Optimizatsiya</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🐍"):
            st.markdown(msg["content"])
            if "time" in msg:
                st.caption(f"🕐 {msg['time']}")

    # Tezkor savol yoki oddiy input
    prompt = st.session_state.get("quick_prompt")
    if prompt:
        st.session_state.quick_prompt = None

    user_input = st.chat_input("Savol bering, kod tashlang yoki xato xabarini yuboring...")
    if user_input:
        prompt = user_input

    if prompt:
        msg_time = format_message_time()
        st.session_state.messages.append({"role": "user", "content": prompt, "time": msg_time})
        st.session_state.total_tokens_used += count_tokens_estimate(prompt)

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.caption(f"🕐 {msg_time}")

        with st.chat_message("assistant", avatar="🐍"):
            placeholder = st.empty()
            full_response = ""
            resp_time = format_message_time()

            try:
                recent = st.session_state.messages[-max_history:]
                if contains_code(prompt):
                    placeholder.markdown("*🔍 Kodingiz tahlil qilinmoqda...*")

                completion = get_ai_response(
                    client, recent, SYSTEM_PROMPTS[mentor_mode],
                    model_choice, temperature, max_tokens, use_streaming
                )

                if use_streaming:
                    for chunk in completion:
                        if chunk.choices and chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                else:
                    with st.spinner("🤔 Javob tayyorlanmoqda..."):
                        full_response = completion.choices[0].message.content
                    placeholder.markdown(full_response)

                st.caption(f"🕐 {resp_time} | 🤖 {model_choice}")
                st.session_state.messages.append({
                    "role": "assistant", "content": full_response,
                    "time": resp_time, "model": model_choice
                })
                st.session_state.total_tokens_used += count_tokens_estimate(full_response)
                st.session_state.conversation_count += 1
                st.session_state.error_count = 0

            except Exception as e:
                err = str(e)
                st.session_state.error_count += 1
                if "rate_limit" in err.lower():
                    st.error("⏱️ Rate limit — 30 soniya kuting.")
                elif "invalid_api_key" in err.lower() or "authentication" in err.lower():
                    st.error("🔑 API kalit noto'g'ri.")
                elif "model_not_found" in err.lower():
                    st.error(f"🤖 Model topilmadi: `{model_choice}`")
                elif "context_length" in err.lower():
                    st.error("📏 Kontekst oshdi — suhbatni tozalang.")
                else:
                    st.error(f"❌ Xatolik: {err}")
                if st.session_state.error_count >= 3:
                    st.warning("⚠️ Bir necha marta xato — API kalitni tekshiring.")

# ============================================================
# TAB 2 — AI COPILOT
# ============================================================
with tab_copilot:

    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        <span style="font-size:28px;">🤖</span>
        <div>
            <span style="color:#e6edf3;font-size:18px;font-weight:700;">AI Copilot</span>
            &nbsp;<span class="copilot-badge">✦ BETA</span>
        </div>
    </div>
    <p style="color:#8b949e;font-size:13px;margin-bottom:20px;">
        GitHub Copilot uslubida: kodingizni <strong style="color:#4f9cf9">yakunlaydi</strong>,
        <strong style="color:#00d4aa">tushuntiradi</strong>,
        <strong style="color:#f0883e">tuzatadi</strong> va
        <strong style="color:#bc8cff">test yozadi</strong>.
    </p>
    """, unsafe_allow_html=True)

    # Amal tanlash
    copilot_action = st.radio(
        "🎯 Qaysi amalni bajarsin?",
        ["✨ Kod yakunlash", "📖 Kodni tushuntirish", "🔧 Xatolarni tuzatish", "🧪 Test yozish"],
        horizontal=True,
        key="copilot_radio"
    )

    # Amallar tavsifi
    action_desc = {
        "✨ Kod yakunlash":      "💡 Tugallanmagan funksiya yoki kodni davom ettiradi, type hints va docstring qo'shadi.",
        "📖 Kodni tushuntirish": "💡 Har bir qatorni O'zbek tilida izohlaydi va complexity tahlil qiladi.",
        "🔧 Xatolarni tuzatish": "💡 Sintaksis, mantiq va runtime xatolarini topib, tuzatilgan kodni beradi.",
        "🧪 Test yozish":        "💡 pytest bilan to'liq unit testlar — edge caseslar bilan.",
    }
    st.caption(action_desc[copilot_action])

    st.markdown("**📝 Kodingizni kiriting:**")
    code_input = st.text_area(
        label="copilot_input",
        label_visibility="collapsed",
        placeholder="# Misol:\ndef fibonacci(n):\n    # davom ettiring...\n",
        height=240,
        key="copilot_code_input"
    )

    col1, col2, col3 = st.columns([2.5, 1, 1])
    with col1:
        run_btn = st.button("🚀  Ishlatish", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️  Tozalash", use_container_width=True)
    with col3:
        if st.session_state.copilot_result:
            fname = "copilot_code.py" if copilot_action != "📖 Kodni tushuntirish" else "copilot_explanation.txt"
            st.download_button(
                "💾  Saqlash",
                st.session_state.copilot_result,
                file_name=fname,
                mime="text/plain",
                use_container_width=True
            )

    if clear_btn:
        st.session_state.copilot_result = ""
        st.session_state.copilot_action_used = ""
        st.rerun()

    if run_btn:
        if not code_input.strip():
            st.warning("⚠️ Iltimos, avval kod kiriting!")
        else:
            action_map = {
                "✨ Kod yakunlash":      (COPILOT_SYSTEM,         "⚡ Kod yakunlanmoqda..."),
                "📖 Kodni tushuntirish": (COPILOT_EXPLAIN_SYSTEM, "📖 Kod tahlil qilinmoqda..."),
                "🔧 Xatolarni tuzatish": (COPILOT_FIX_SYSTEM,     "🔧 Xatolar tuzatilmoqda..."),
                "🧪 Test yozish":        (COPILOT_TEST_SYSTEM,     "🧪 Testlar yozilmoqda..."),
            }
            system_p, spinner_text = action_map[copilot_action]

            with st.spinner(spinner_text):
                try:
                    result = copilot_call(client, code_input, system_p, model_choice)
                    st.session_state.copilot_result = result
                    st.session_state.copilot_action_used = copilot_action
                    st.session_state.total_tokens_used += count_tokens_estimate(code_input + result)
                except Exception as e:
                    err = str(e)
                    if "rate_limit" in err.lower():
                        st.error("⏱️ Rate limit — biroz kuting.")
                    elif "context_length" in err.lower():
                        st.error("📏 Kod juda uzun — qisqartiring.")
                    else:
                        st.error(f"❌ Xatolik: {err}")

    # ---- Natija ----
    if st.session_state.copilot_result:
        st.markdown("---")

        label_map = {
            "✨ Kod yakunlash":      "✨ Yakunlangan kod",
            "📖 Kodni tushuntirish": "📖 Tushuntirish",
            "🔧 Xatolarni tuzatish": "🔧 Tuzatilgan kod",
            "🧪 Test yozish":        "🧪 Test kodi",
        }
        used = st.session_state.copilot_action_used or copilot_action
        st.markdown(f"**{label_map.get(used, '📄 Natija')}:**")

        if used == "📖 Kodni tushuntirish":
            st.markdown(
                f'<div class="copilot-suggestion">{st.session_state.copilot_result}</div>',
                unsafe_allow_html=True
            )
        else:
            st.code(st.session_state.copilot_result, language="python")

        # Chat ga yuborish
        st.markdown("")
        if st.button("💬  Natijani Chat Mentor ga yuborish"):
            suffix = "kodi" if used != "📖 Kodni tushuntirish" else "tahlili"
            content = (
                f"**Copilot {suffix}** ({used}):\n\n"
                f"```python\n{st.session_state.copilot_result}\n```"
                if used != "📖 Kodni tushuntirish"
                else f"**Copilot tushuntirishi:**\n\n{st.session_state.copilot_result}"
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": content,
                "time": format_message_time(),
                "model": model_choice
            })
            st.success("✅ Chat Mentor ga yuborildi! '💬 Chat Mentor' tabiga o'ting.")

    # ---- Qo'llanma ----
    with st.expander("📘 Copilot qo'llanmasi — qanday ishlatish kerak?"):
        st.markdown("""
### ✨ Kod yakunlash
Tugallanmagan funksiya yoki klassni kiriting:
```python
def merge_sort(arr):
    # shu yerdan davom ettirsin
```
→ Copilot to'liq implementatsiya, type hints va docstring bilan qaytaradi.

---
### 📖 Kodni tushuntirish
Tushunmagan kodingizni kiriting — Copilot har qatorni O'zbek tilida izohlaydi.

---
### 🔧 Xatolarni tuzatish
Xatoli kodni kiriting:
```python
def divide(a, b):
    return a / b   # ZeroDivisionError!
```
→ Copilot xatoni topib, tuzatilgan versiyasini beradi.

---
### 🧪 Test yozish
Istalgan funksiyangizni kiriting — Copilot `pytest` testlarini yozadi.

---
💡 **Maslahat:** Katta model `llama-3.3-70b-versatile` = eng aniq natija.
        """)
