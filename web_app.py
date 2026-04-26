"""
AI Python Mentor PRO - v4.0
Muallif: Jaloliddin | Magistr/Researcher
Yangiliklar:
  - 🏆 Quiz rejimi
  - 📝 Suhbat tarixi (saqlash/yuklash)
  - 🌐 Tarjima (Ingliz/Rus/O'zbek)
  - 🗂️ Loyiha strukturasi tahlili
  - 🖥️ Code Runner (Piston API)
  - 📊 Dashboard statistika
  - 🌙 Light/Dark tema
  - 🔄 Refactoring, 📦 Kutubxona tavsiya, 🔐 Xavfsizlik skaneri
  - ⚡ Copilot auto-suggest
  - 🔔 Ovozli bildirishnoma
"""

import streamlit as st
from groq import Groq
import time, json, random, requests
from datetime import datetime

# ─────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Python Mentor PRO",
    layout="wide",
    page_icon="🐍",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI Python Mentor v4.0 PRO | Jaloliddin | Magistr/Researcher"}
)

# ─────────────────────────────────────────────
# 2. GROQ CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        return None, None
    try:
        return Groq(api_key=api_key), api_key
    except Exception as e:
        return None, None

client, api_key = get_groq_client()

# ─────────────────────────────────────────────
# 3. SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS = {
    "messages": [],
    "total_tokens": 0,
    "session_start": datetime.now().strftime("%H:%M"),
    "conversation_count": 0,
    "error_count": 0,
    "copilot_result": "",
    "copilot_action_used": "",
    "quick_prompt": None,
    "theme": "dark",
    "saved_sessions": [],          # [{name, messages, date}]
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_question": None,
    "quiz_answered": False,
    "dashboard_api_calls": [],     # [{"time": ..., "tokens": ...}]
    "runner_output": "",
    "runner_error": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# 4. TEMA
# ─────────────────────────────────────────────
IS_DARK = st.session_state.theme == "dark"

THEME = {
    "bg_primary":   "#0d1117" if IS_DARK else "#f6f8fa",
    "bg_secondary": "#161b22" if IS_DARK else "#ffffff",
    "bg_card":      "#1c2128" if IS_DARK else "#f0f3f6",
    "text_primary": "#e6edf3" if IS_DARK else "#1c2128",
    "text_secondary":"#8b949e" if IS_DARK else "#57606a",
    "border":       "#30363d" if IS_DARK else "#d0d7de",
    "accent_green": "#00d4aa",
    "accent_blue":  "#4f9cf9",
    "accent_purple":"#bc8cff",
    "accent_orange":"#f0883e",
}
T = THEME

# ─────────────────────────────────────────────
# 5. CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
:root {{
    --bg-p:  {T['bg_primary']};   --bg-s:  {T['bg_secondary']};
    --bg-c:  {T['bg_card']};      --txt-p: {T['text_primary']};
    --txt-s: {T['text_secondary']};--bdr:  {T['border']};
    --green: {T['accent_green']}; --blue:  {T['accent_blue']};
    --purple:{T['accent_purple']};--orange:{T['accent_orange']};
}}
.stApp {{ background:var(--bg-p) !important; font-family:'Inter',sans-serif; color:var(--txt-p) !important; }}
h1,h2,h3 {{ color:var(--txt-p) !important; }}
h1 {{ background:linear-gradient(135deg,var(--green),var(--blue));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700 !important; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background:var(--bg-s) !important; border-radius:10px !important;
    padding:4px !important; border:1px solid var(--bdr) !important; gap:3px !important;
    flex-wrap:wrap !important;
}}
.stTabs [data-baseweb="tab"] {{
    color:var(--txt-s) !important; font-weight:500 !important;
    border-radius:8px !important; padding:7px 14px !important;
    font-family:'Inter',sans-serif !important; font-size:13px !important;
}}
.stTabs [aria-selected="true"] {{
    background:linear-gradient(135deg,var(--green),var(--blue)) !important;
    color:#000 !important; font-weight:700 !important;
}}

/* Chat */
.stChatMessage {{ background:var(--bg-s) !important; border:1px solid var(--bdr) !important;
    border-radius:12px !important; margin-bottom:8px !important; }}
[data-testid="stChatMessageContent"] {{
    color:var(--txt-p) !important; font-family:'Inter',sans-serif !important;
    font-size:14px !important; line-height:1.7 !important;
}}
.stChatInputContainer {{ background:var(--bg-s) !important; border:1px solid var(--bdr) !important; border-radius:12px !important; }}
.stChatInputContainer textarea {{ color:var(--txt-p) !important; background:transparent !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background:var(--bg-s) !important; border-right:1px solid var(--bdr) !important; }}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{ color:var(--txt-p) !important; }}

/* Widgets */
[data-testid="stMetric"] {{ background:var(--bg-c) !important; border:1px solid var(--bdr) !important; border-radius:8px !important; padding:12px !important; }}
[data-testid="stMetricValue"] {{ color:var(--txt-p) !important; }}
.stSelectbox > div > div {{ background:var(--bg-c) !important; border:1px solid var(--bdr) !important; color:var(--txt-p) !important; border-radius:8px !important; }}
.stTextArea textarea {{ background:var(--bg-c) !important; color:var(--txt-p) !important;
    border:1px solid var(--bdr) !important; border-radius:8px !important;
    font-family:'JetBrains Mono',monospace !important; font-size:13px !important; }}
.stTextInput input {{ background:var(--bg-c) !important; color:var(--txt-p) !important;
    border:1px solid var(--bdr) !important; border-radius:8px !important; }}

/* Buttons */
.stButton > button {{
    background:linear-gradient(135deg,var(--green),var(--blue)) !important;
    color:#000 !important; font-weight:600 !important; border:none !important;
    border-radius:8px !important; transition:all 0.2s !important;
}}
.stButton > button:hover {{ transform:translateY(-1px) !important; box-shadow:0 4px 20px rgba(0,212,170,.3) !important; }}

/* Code */
code {{ background:var(--bg-c) !important; color:var(--green) !important;
    font-family:'JetBrains Mono',monospace !important; border-radius:4px !important; padding:2px 6px !important; }}
pre {{ background:var(--bg-c) !important; border:1px solid var(--bdr) !important;
    border-radius:8px !important; padding:16px !important; font-family:'JetBrains Mono',monospace !important; }}

/* Cards */
.card {{ background:var(--bg-s); border:1px solid var(--bdr); border-radius:12px; padding:20px; margin-bottom:12px; }}
.card-blue  {{ border-left:3px solid var(--blue); background:rgba(79,156,249,.05); border-radius:10px; padding:16px; }}
.card-green {{ border-left:3px solid var(--green); background:rgba(0,212,170,.05); border-radius:10px; padding:16px; }}
.card-orange{{ border-left:3px solid var(--orange); background:rgba(240,136,62,.05); border-radius:10px; padding:16px; }}
.card-purple{{ border-left:3px solid var(--purple); background:rgba(188,140,255,.05); border-radius:10px; padding:16px; }}

/* Quiz */
.quiz-card {{ background:var(--bg-s); border:1px solid var(--bdr); border-radius:14px; padding:24px; }}
.quiz-option {{ background:var(--bg-c); border:1px solid var(--bdr); border-radius:8px;
    padding:10px 16px; margin:6px 0; cursor:pointer; transition:all 0.2s;
    color:var(--txt-p); font-size:14px; }}
.quiz-correct  {{ border-color:#3fb950 !important; background:rgba(63,185,80,.1) !important; }}
.quiz-wrong    {{ border-color:#f85149 !important; background:rgba(248,81,73,.1) !important; }}

/* Runner output */
.runner-output {{ background:#0d1117; border:1px solid var(--bdr); border-radius:8px;
    padding:16px; font-family:'JetBrains Mono',monospace; font-size:13px;
    color:#00d4aa; min-height:60px; white-space:pre-wrap; }}
.runner-error  {{ color:#f85149; }}

/* Badges */
.badge {{ display:inline-flex; align-items:center; gap:5px; border-radius:20px;
    padding:3px 10px; font-size:11px; font-weight:700; letter-spacing:.5px; }}
.badge-green  {{ background:rgba(63,185,80,.1);  border:1px solid rgba(63,185,80,.3);  color:#3fb950; }}
.badge-blue   {{ background:rgba(79,156,249,.1);  border:1px solid rgba(79,156,249,.3);  color:var(--blue); }}
.badge-purple {{ background:rgba(188,140,255,.1); border:1px solid rgba(188,140,255,.3); color:var(--purple); }}
.badge-orange {{ background:rgba(240,136,62,.1);  border:1px solid rgba(240,136,62,.3);  color:var(--orange); }}

/* Status */
.status-badge {{ display:inline-flex; align-items:center; gap:6px;
    background:rgba(63,185,80,.1); border:1px solid rgba(63,185,80,.3);
    border-radius:20px; padding:4px 12px; font-size:12px; color:#3fb950; font-weight:500; }}
.status-dot {{ width:6px; height:6px; background:#3fb950; border-radius:50%; animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}

/* Mobile */
@media (max-width:768px) {{
    .stTabs [data-baseweb="tab"] {{ padding:6px 10px !important; font-size:12px !important; }}
    h1 {{ font-size:20px !important; }}
}}

hr {{ border-color:var(--bdr) !important; margin:16px 0 !important; }}
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:var(--bg-p); }}
::-webkit-scrollbar-thumb {{ background:var(--bdr); border-radius:3px; }}

/* Audio notification (hidden) */
#audio-notify {{ display:none; }}
</style>

<!-- Audio notification -->
<audio id="audio-notify">
  <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAA..." type="audio/wav">
</audio>
<script>
function playNotify() {{
    try {{
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.value = 880; osc.type = 'sine';
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
        osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.4);
    }} catch(e) {{}}
}}
// Watch for new assistant messages
const observer = new MutationObserver(() => {{
    const el = document.getElementById('notify-trigger');
    if (el && el.dataset.notify === '1') {{ playNotify(); el.dataset.notify = '0'; }}
}});
observer.observe(document.body, {{ subtree:true, attributes:true }});
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 6. SYSTEM PROMPTS
# ─────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "Python Mentor 🐍": """Sen magistr darajasidagi tajribali Python arxitektisan va mentorsan.
Vazifang: Kod tahlili (Big-O, PEP8, SOLID), xavfsizlik zaifliklarini topish,
optimizatsiya va best practices tavsiya qilish. Javoblaring aniq, kod namunali,
O'zbek tilida bo'lsin.""",

    "Code Reviewer 🔍": """Sen yuqori malakali Code Reviewer san.
Format: ## 📊 Baho X/10 | ✅ Yaxshi | ⚠️ Kamchilik | 🔧 Yaxshilangan kod | 📈 Complexity.
Faqat O'zbek tilida.""",

    "Debug Ustasi 🐛": """Sen Python debug ekspertisan.
Format: 🔍 Sabab → 📍 Joy → 🔧 Yechim → 💡 Oldini olish → ✅ Tuzatilgan kod.
Faqat O'zbek tilida.""",

    "Algoritm Muallimi 📚": """Sen DSA professor san.
Format: Nazariya → ASCII vizual → Python kod → Complexity → Mashq.
Faqat O'zbek tilida.""",
}

COPILOT_PROMPTS = {
    "✨ Yakunlash":    "Faqat Python kodi ber. Tugallanmagan kodni davom ettir. Type hints + docstring. Markdown ``` yo'q.",
    "📖 Tushuntirish": "O'zbek tilida har qatorni izohlash. Complexity qo'sh.",
    "🔧 Tuzatish":     "Xatolarni tuzat. Avval tuzatilgan kod, keyin O'zbek tilida nima o'zgardi.",
    "🧪 Test":         "pytest unit testlar. Edge caseslar. O'zbek tilida qisqa izoh.",
    "🔄 Refactoring":  "Kodni qayta yoz: clean code, SOLID, pattern. Avval yangi kod, keyin O'zbek tilida farqlar.",
    "📦 Kutubxona":    "Bu vazifa uchun eng yaxshi Python kutubxonalar. O'zbek tilida: nomi, sababi, pip install, misol.",
    "🔐 Xavfsizlik":   "Kodda xavfsizlik zaifliklarini top. O'zbek tilida: zaiflik turi, xavf darajasi, tuzatilgan kod.",
}

TRANSLATE_PROMPT = {
    "🇬🇧 Inglizcha": "Translate the following O'zbek text to English. Return only the translation.",
    "🇷🇺 Ruscha":    "Переведи следующий узбекский текст на русский. Верни только перевод.",
    "🇺🇿 O'zbekcha": "Translate the following text to Uzbek (Latin script). Return only the translation.",
}

# ─────────────────────────────────────────────
# 7. QUIZ SAVOLLAR BANKI
# ─────────────────────────────────────────────
QUIZ_BANK = [
    {"q":"Python'da `is` va `==` operatorlari farqi nima?",
     "opts":["Ikkalasi bir xil","is — ob'ekt identifikatori, == — qiymat tengligini tekshiradi",
             "== — ob'ekt identifikatori, is — qiymatni tekshiradi","Faqat son uchun ishlatiladi"],
     "ans":1,"exp":"is operator ikki o'zgaruvchi bir xil ob'ektga ishora qilishini tekshiradi (id()), == esa qiymatlarni solishtiradi."},
    {"q":"Quyidagi kod nima qaytaradi?\n```python\nprint(type([]) == type(()))```",
     "opts":["True","False","TypeError","None"],
     "ans":1,"exp":"[] list, () tuple — turli tiplar, shuning uchun False."},
    {"q":"Python GIL nima?",
     "opts":["Global Import Lock","Global Interpreter Lock","General Input Library","None"],
     "ans":1,"exp":"GIL (Global Interpreter Lock) — bir vaqtda faqat bitta thread Python bytekodini bajarishi mumkin."},
    {"q":"`*args` va `**kwargs` farqi?",
     "opts":["Farqi yo'q","*args — ro'yxat, **kwargs — lug'at","*args — n ta positional, **kwargs — n ta keyword argument","Faqat class methodlarida ishlatiladi"],
     "ans":2,"exp":"*args ixtiyoriy positional argumentlarni tuple sifatida, **kwargs ixtiyoriy keyword argumentlarni dict sifatida qabul qiladi."},
    {"q":"List comprehension vs for loop — qaysi tezroq?",
     "opts":["For loop","List comprehension","Teng","Faqat kichik listlarda tezroq"],
     "ans":1,"exp":"List comprehension C darajasida optimallashtirilgan, oddiy for loopdan 35-50% tezroq ishlaydi."},
    {"q":"Python'da `__slots__` nima uchun ishlatiladi?",
     "opts":["Magic method","Xotira tejash uchun — __dict__ o'rniga","Import tezlatish","Faqat dataclass da"],
     "ans":1,"exp":"__slots__ ob'ekt atributlarini dict o'rniga static arrayda saqlaydi — xotira 40-50% kam sarflanadi."},
    {"q":"`@staticmethod` va `@classmethod` farqi?",
     "opts":["Farqi yo'q","@staticmethod — na self, na cls; @classmethod — cls oladi",
             "@classmethod — na self, na cls; @staticmethod — cls oladi","Ikkalasi ham self oladi"],
     "ans":1,"exp":"@staticmethod oddiy funksiya kabi, classga bog'liq emas. @classmethod cls (class reference) oladi."},
    {"q":"Python'da `deepcopy` va `copy` farqi?",
     "opts":["Farqi yo'q","deepcopy — ichki ob'ektlarni ham nusxalaydi, copy — faqat tashqi","copy — ichki ob'ektlarni ham nusxalaydi","Faqat list uchun ishlaydi"],
     "ans":1,"exp":"copy.copy() — shallow: ichki ob'ektlar hali ham reference. copy.deepcopy() — deep: barcha ichki ob'ektlar ham yangi nusxa."},
    {"q":"Generator va List farqi?",
     "opts":["Farqi yo'q","Generator — lazy evaluation, xotira tejaydi","List — lazy evaluation","Generator tezroq, ammo ko'proq xotira"],
     "ans":1,"exp":"Generator yield bilan ishlaydi — qiymatlar bittadan hisoblanadi. 1M element: list ~8MB, generator ~120 byte."},
    {"q":"Python'da `with` statement nima uchun?",
     "opts":["Faqat fayl uchun","Context manager — resursni avtomatik yopish/tozalash","Try/except o'rnini bosadi","Import qilish uchun"],
     "ans":1,"exp":"with statement __enter__ va __exit__ methodlarini chaqiradi. Fayl, DB connection, lock kabilarni xavfsiz boshqaradi."},
]

# ─────────────────────────────────────────────
# 8. HELPER FUNKSIYALAR
# ─────────────────────────────────────────────
def count_tokens(text: str) -> int:
    return len(text) // 4

def contains_code(text: str) -> bool:
    return any(k in text for k in ["```","def ","import ","class ","for ","while ","=>"])

def fmt_time() -> str:
    return datetime.now().strftime("%H:%M")

def export_session() -> str:
    return json.dumps({
        "version": "4.0",
        "export_time": datetime.now().isoformat(),
        "session_start": st.session_state.session_start,
        "total_messages": len(st.session_state.messages),
        "messages": st.session_state.messages
    }, ensure_ascii=False, indent=2)

def ai_call(messages_for_api: list, model: str, temperature: float,
            max_tokens: int, streaming: bool):
    """Clean API call — faqat role+content."""
    return client.chat.completions.create(
        model=model, messages=messages_for_api,
        stream=streaming, temperature=temperature,
        max_tokens=max_tokens, top_p=0.9,
        frequency_penalty=0.1, presence_penalty=0.1,
    )

def chat_ai(messages: list, system: str, model: str,
            temperature: float, max_tokens: int, streaming: bool):
    clean = [{"role": m["role"], "content": m["content"]} for m in messages]
    return ai_call([{"role":"system","content":system}] + clean,
                   model, temperature, max_tokens, streaming)

def simple_ai(prompt: str, system: str, model: str, temperature: float = 0.2) -> str:
    resp = ai_call([{"role":"system","content":system},
                    {"role":"user","content":prompt}],
                   model, temperature, 2048, False)
    return resp.choices[0].message.content

def run_code_piston(code: str) -> tuple[str, str]:
    """Piston API orqali Python kodni bajarish (bepul, serverless)."""
    try:
        r = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={"language":"python","version":"3.10.0",
                  "files":[{"name":"main.py","content":code}]},
            timeout=15
        )
        data = r.json()
        run = data.get("run", {})
        return run.get("stdout",""), run.get("stderr","")
    except requests.exceptions.Timeout:
        return "", "⏱️ Timeout — kod 15 soniyadan ko'p vaqt oldi."
    except Exception as e:
        return "", f"❌ Runner xatolik: {e}"

def log_api_call(tokens: int):
    st.session_state.dashboard_api_calls.append({
        "time": fmt_time(), "tokens": tokens,
        "date": datetime.now().strftime("%H:%M:%S")
    })

# ─────────────────────────────────────────────
# 9. SARLAVHA
# ─────────────────────────────────────────────
col_title, col_theme, col_status = st.columns([3, 0.8, 0.8])
with col_title:
    st.title("🐍 AI Python Mentor PRO")
    st.caption("v4.0 | Magistratura darajasidagi intellektual dasturlash yordamchisi")
with col_theme:
    if st.button("🌙 Dark" if not IS_DARK else "☀️ Light", use_container_width=True):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()
with col_status:
    if api_key:
        st.markdown('<div class="status-badge"><span class="status-dot"></span>Online</div>',
                    unsafe_allow_html=True)
    else:
        st.error("Offline")
st.divider()

# ─────────────────────────────────────────────
# 10. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Sozlamalar")
    mentor_mode   = st.selectbox("🎯 Mentor rejimi", list(SYSTEM_PROMPTS.keys()))
    model_choice  = st.selectbox("🤖 Model", [
        "llama-3.3-70b-versatile","llama-3.1-8b-instant",
        "mixtral-8x7b-32768","gemma2-9b-it"])
    temperature   = st.slider("🌡️ Ijodkorlik", 0.0, 1.0, 0.7, 0.1)
    max_tokens    = st.select_slider("📏 Javob uzunligi", [512,1024,2048,4096,8192], value=2048)
    max_history   = st.slider("💬 Tariх uzunligi", 2, 30, 10, 2)
    use_streaming = st.toggle("⚡ Streaming", value=True)
    notify_sound  = st.toggle("🔔 Ovozli xabar", value=True)

    st.divider()
    st.markdown("### 📊 Sessiya")
    c1,c2 = st.columns(2)
    c1.metric("💬 Xabar", len(st.session_state.messages))
    c2.metric("🔄 Suhbat", st.session_state.conversation_count)
    st.metric("🪙 Token", f"~{st.session_state.total_tokens:,}")
    st.metric("🏆 Quiz", f"{st.session_state.quiz_score}/{st.session_state.quiz_total}")

    st.divider()
    st.markdown("### 💾 Sessiya boshqaruvi")
    session_name = st.text_input("Sessiya nomi", placeholder="Mening suhbatim...")
    if st.button("💾 Saqlab qo'yish", use_container_width=True):
        if st.session_state.messages:
            name = session_name or f"Sessiya {datetime.now().strftime('%d/%m %H:%M')}"
            st.session_state.saved_sessions.append({
                "name": name,
                "messages": st.session_state.messages.copy(),
                "date": fmt_time(),
                "count": len(st.session_state.messages)
            })
            st.success(f"✅ '{name}' saqlandi!")
        else:
            st.warning("Suhbat bo'sh!")

    if st.session_state.saved_sessions:
        names = [s["name"] for s in st.session_state.saved_sessions]
        sel = st.selectbox("📂 Yuklash", ["— tanlang —"] + names)
        if sel != "— tanlang —" and st.button("📂 Yuklash", use_container_width=True):
            s = next(x for x in st.session_state.saved_sessions if x["name"] == sel)
            st.session_state.messages = s["messages"].copy()
            st.success(f"✅ '{sel}' yuklandi!")
            st.rerun()

    st.divider()
    if st.button("🗑️ Suhbatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.session_state.conversation_count = 0
        st.session_state.copilot_result = ""
        st.session_state.runner_output = ""
        st.session_state.runner_error  = ""
        st.success("✅ Tozalandi!")
        time.sleep(0.4); st.rerun()

    if st.session_state.messages:
        st.download_button("📥 JSON eksport", export_session(),
            f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            "application/json", use_container_width=True)

    st.divider()
    st.markdown("### 💡 Tezkor savollar")
    for q in ["list vs tuple?","GIL nima?","Decorator?","async/await?","Generator vs Iterator?"]:
        if st.button(q, use_container_width=True, key=f"q_{q}"):
            st.session_state.quick_prompt = q
            st.rerun()

    st.divider()
    st.markdown(f'<p style="color:{T["text_secondary"]};font-size:11px;text-align:center">'
                '🐍 v4.0 PRO | Jaloliddin<br>Magistr/Researcher</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 11. API KEY CHECK
# ─────────────────────────────────────────────
if not api_key:
    st.warning("⚠️ `GROQ_API_KEY` ni Streamlit Secrets ga qo'shing.")
    st.code('# .streamlit/secrets.toml\nGROQ_API_KEY = "gsk_your_key_here"', language="toml")
    st.info("🔑 Bepul: https://console.groq.com")
    st.stop()

# ─────────────────────────────────────────────
# 12. TABLAR
# ─────────────────────────────────────────────
tabs = st.tabs([
    "💬 Chat",
    "🤖 Copilot",
    "🖥️ Runner",
    "🏆 Quiz",
    "🌐 Tarjima",
    "📊 Dashboard",
])
tab_chat, tab_copilot, tab_runner, tab_quiz, tab_translate, tab_dashboard = tabs

# ══════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════
with tab_chat:
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="text-align:center;padding:36px 20px;color:{T['text_secondary']};">
            <h2 style="color:{T['text_primary']};font-size:22px;">Salom! Men sizning AI Python Mentoringizman 👋</h2>
            <p style="font-size:14px;max-width:540px;margin:0 auto 20px;">
                Savol bering, kod tashlang yoki 6 ta tabdan birini tanlang.
            </p>
            <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
                <span style="background:{T['bg_card']};border:1px solid {T['border']};border-radius:8px;padding:7px 14px;font-size:12px;color:{T['text_primary']};">🔍 Kod tahlili</span>
                <span style="background:{T['bg_card']};border:1px solid {T['border']};border-radius:8px;padding:7px 14px;font-size:12px;color:{T['text_primary']};">🐛 Debug</span>
                <span style="background:{T['bg_card']};border:1px solid {T['border']};border-radius:8px;padding:7px 14px;font-size:12px;color:{T['text_primary']};">📚 Algoritm</span>
                <span style="background:{T['bg_card']};border:1px solid {T['border']};border-radius:8px;padding:7px 14px;font-size:12px;color:{T['text_primary']};">⚡ Optim.</span>
            </div>
        </div>""", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🐍"):
            st.markdown(msg["content"])
            if "time" in msg:
                st.caption(f"🕐 {msg['time']}")

    prompt = st.session_state.get("quick_prompt")
    if prompt:
        st.session_state.quick_prompt = None
    user_input = st.chat_input("Savol bering yoki kod tashlang...")
    if user_input:
        prompt = user_input

    if prompt:
        t = fmt_time()
        st.session_state.messages.append({"role":"user","content":prompt,"time":t})
        st.session_state.total_tokens += count_tokens(prompt)

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.caption(f"🕐 {t}")

        with st.chat_message("assistant", avatar="🐍"):
            ph = st.empty()
            full = ""
            rt = fmt_time()
            try:
                recent = st.session_state.messages[-max_history:]
                if contains_code(prompt):
                    ph.markdown("*🔍 Tahlil qilinmoqda...*")

                comp = chat_ai(recent, SYSTEM_PROMPTS[mentor_mode],
                               model_choice, temperature, max_tokens, use_streaming)
                if use_streaming:
                    for chunk in comp:
                        if chunk.choices and chunk.choices[0].delta.content:
                            full += chunk.choices[0].delta.content
                            ph.markdown(full + "▌")
                    ph.markdown(full)
                else:
                    with st.spinner("🤔 Tayyorlanmoqda..."):
                        full = comp.choices[0].message.content
                    ph.markdown(full)

                st.caption(f"🕐 {rt} | 🤖 {model_choice}")
                st.session_state.messages.append({"role":"assistant","content":full,"time":rt,"model":model_choice})
                st.session_state.total_tokens += count_tokens(full)
                st.session_state.conversation_count += 1
                log_api_call(count_tokens(prompt + full))
                st.session_state.error_count = 0

                # Ovozli bildirishnoma trigger
                if notify_sound:
                    st.markdown('<div id="notify-trigger" data-notify="1"></div>', unsafe_allow_html=True)

            except Exception as e:
                err = str(e)
                st.session_state.error_count += 1
                if "rate_limit"   in err.lower(): st.error("⏱️ Rate limit — 30 soniya kuting.")
                elif "api_key"    in err.lower(): st.error("🔑 API kalit noto'g'ri.")
                elif "model_not"  in err.lower(): st.error(f"🤖 Model topilmadi: `{model_choice}`")
                elif "context_len"in err.lower(): st.error("📏 Kontekst oshdi — suhbatni tozalang.")
                else: st.error(f"❌ {err}")

# ══════════════════════════════════════════════
# TAB 2 — COPILOT
# ══════════════════════════════════════════════
with tab_copilot:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <span style="font-size:26px;">🤖</span>
        <span style="color:{T['text_primary']};font-size:18px;font-weight:700;">AI Copilot</span>
        <span class="badge badge-purple">✦ v2</span>
    </div>
    <p style="color:{T['text_secondary']};font-size:13px;margin-bottom:16px;">
        7 ta amal: yakunlash · tushuntirish · tuzatish · test · refactoring · kutubxona · xavfsizlik
    </p>""", unsafe_allow_html=True)

    copilot_action = st.radio(
        "🎯 Amal:", list(COPILOT_PROMPTS.keys()), horizontal=True)

    action_hints = {
        "✨ Yakunlash":  "Tugallanmagan funksiya/klassni type hints + docstring bilan yakunlaydi.",
        "📖 Tushuntirish":"Har qatorni O'zbek tilida izohlaydi + Big-O tahlili.",
        "🔧 Tuzatish":   "Sintaksis/mantiq/runtime xatolarini topib tuzatadi.",
        "🧪 Test":       "pytest unit testlar — edge caseslar bilan.",
        "🔄 Refactoring":"Clean code + SOLID + design patterns.",
        "📦 Kutubxona":  "Vazifaga mos eng yaxshi kutubxonalarni tavsiya qiladi.",
        "🔐 Xavfsizlik": "OWASP zaifliklarini skanerlaydi, xavf darajasi ko'rsatadi.",
    }
    st.caption(action_hints.get(copilot_action, ""))

    code_input = st.text_area("📝 Kodingizni kiriting:",
        placeholder="def fibonacci(n):\n    # davom ettiring...",
        height=220, label_visibility="visible")

    c1,c2,c3 = st.columns([2,1,1])
    with c1: run_btn   = st.button("🚀 Ishlatish", use_container_width=True)
    with c2: clear_btn = st.button("🗑️ Tozalash", use_container_width=True)
    with c3:
        if st.session_state.copilot_result:
            ext = ".txt" if "Tushuntirish" in st.session_state.copilot_action_used else ".py"
            st.download_button("💾 Saqlash", st.session_state.copilot_result,
                f"copilot{ext}", "text/plain", use_container_width=True)

    if clear_btn:
        st.session_state.copilot_result = ""
        st.rerun()

    if run_btn:
        if not code_input.strip():
            st.warning("⚠️ Kod kiriting!")
        else:
            spinners = {
                "✨ Yakunlash":"⚡ Yakunlanmoqda...","📖 Tushuntirish":"📖 Tahlil qilinmoqda...",
                "🔧 Tuzatish":"🔧 Tuzatilmoqda...","🧪 Test":"🧪 Test yozilmoqda...",
                "🔄 Refactoring":"🔄 Refactoring...",
                "📦 Kutubxona":"📦 Kutubxonalar qidirilmoqda...","🔐 Xavfsizlik":"🔐 Skanerlash...",
            }
            with st.spinner(spinners.get(copilot_action,"⚙️ Ishlanmoqda...")):
                try:
                    result = simple_ai(code_input, COPILOT_PROMPTS[copilot_action], model_choice)
                    st.session_state.copilot_result     = result
                    st.session_state.copilot_action_used = copilot_action
                    st.session_state.total_tokens += count_tokens(code_input + result)
                    log_api_call(count_tokens(code_input + result))
                except Exception as e:
                    st.error(f"❌ {e}")

    if st.session_state.copilot_result:
        st.divider()
        used = st.session_state.copilot_action_used
        st.markdown(f"**{used} natijasi:**")

        if "Tushuntirish" in used or "Kutubxona" in used or "Xavfsizlik" in used:
            card_cls = {"Tushuntirish":"card-green","Kutubxona":"card-blue","Xavfsizlik":"card-orange"}
            cls = next((v for k,v in card_cls.items() if k in used), "card-blue")
            st.markdown(f'<div class="{cls}" style="color:{T["text_primary"]}">'
                        f'{st.session_state.copilot_result}</div>', unsafe_allow_html=True)
        else:
            st.code(st.session_state.copilot_result, language="python")

        if st.button("💬 Chat ga yuborish"):
            is_code = "Tushuntirish" not in used
            content = (f"**Copilot ({used}):**\n```python\n{st.session_state.copilot_result}\n```"
                       if is_code else
                       f"**Copilot tushuntirishi:**\n{st.session_state.copilot_result}")
            st.session_state.messages.append({"role":"assistant","content":content,
                                              "time":fmt_time(),"model":model_choice})
            st.success("✅ Chat ga yuborildi!")

    with st.expander("📘 Copilot qo'llanmasi"):
        st.markdown("""
**✨ Yakunlash** — `def func():  # shu yerdan` → to'liq implementatsiya
**📖 Tushuntirish** — har qator izohli + Time/Space complexity
**🔧 Tuzatish** — `a / b` → `a / b if b != 0 else None`
**🧪 Test** — `def test_func(): assert func(2) == 4`
**🔄 Refactoring** — God function → kichik funksiyalar, SOLID
**📦 Kutubxona** — "HTTP so'rov" → `httpx`, `aiohttp`, `requests`
**🔐 Xavfsizlik** — SQL injection, path traversal, secrets in code

💡 Katta model = aniqroq natija
        """)

# ══════════════════════════════════════════════
# TAB 3 — CODE RUNNER
# ══════════════════════════════════════════════
with tab_runner:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <span style="font-size:26px;">🖥️</span>
        <span style="color:{T['text_primary']};font-size:18px;font-weight:700;">Code Runner</span>
        <span class="badge badge-green">Piston API</span>
    </div>
    <p style="color:{T['text_secondary']};font-size:13px;margin-bottom:16px;">
        Python 3.10 kodni brauzerda bajarish — Piston API orqali (bepul, serverless)
    </p>""", unsafe_allow_html=True)

    runner_code = st.text_area(
        "📝 Python kodi:",
        value='# Misol:\nfor i in range(1, 6):\n    print(f"Fibonacci: {i}")\n\nprint("Tayyor! ✅")',
        height=260,
        key="runner_code_input"
    )

    col_run, col_clear, col_copy = st.columns([2,1,1])
    with col_run:
        run_code_btn = st.button("▶️ Kodni bajarish", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Tozalash", use_container_width=True, key="runner_clear"):
            st.session_state.runner_output = ""
            st.session_state.runner_error  = ""
            st.rerun()
    with col_copy:
        # Copilot ga yuborish
        if st.button("🤖 Copilot ga", use_container_width=True):
            st.session_state["copilot_from_runner"] = runner_code
            st.info("Copilot tabiga o'ting va kodni tashlang!")

    if run_code_btn and runner_code.strip():
        with st.spinner("⚙️ Kod bajarilmoqda..."):
            out, err = run_code_piston(runner_code)
            st.session_state.runner_output = out
            st.session_state.runner_error  = err

    if st.session_state.runner_output or st.session_state.runner_error:
        st.markdown("**📤 Natija:**")
        if st.session_state.runner_output:
            st.markdown(
                f'<div class="runner-output">{st.session_state.runner_output}</div>',
                unsafe_allow_html=True
            )
        if st.session_state.runner_error:
            st.markdown(
                f'<div class="runner-output runner-error">⚠️ Xatolik:\n{st.session_state.runner_error}</div>',
                unsafe_allow_html=True
            )
            # Xatoni avtomatik tuzatish
            if st.button("🔧 Xatoni Copilot bilan tuzatish"):
                with st.spinner("🔧 Tuzatilmoqda..."):
                    try:
                        fixed = simple_ai(
                            f"Kod:\n{runner_code}\n\nXatolik:\n{st.session_state.runner_error}",
                            COPILOT_PROMPTS["🔧 Tuzatish"], model_choice
                        )
                        st.session_state.copilot_result = fixed
                        st.session_state.copilot_action_used = "🔧 Tuzatish"
                        st.success("✅ Tuzatildi! Copilot tabiga o'ting.")
                    except Exception as e:
                        st.error(f"❌ {e}")

    st.markdown("---")
    st.markdown(f'<p style="color:{T["text_secondary"]};font-size:12px;">ℹ️ Piston API: Python 3.10 • Max 15s • Internet kirish yo\'q • stdin qo\'llab-quvvatlanmaydi</p>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — QUIZ
# ══════════════════════════════════════════════
with tab_quiz:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <span style="font-size:26px;">🏆</span>
        <span style="color:{T['text_primary']};font-size:18px;font-weight:700;">Python Quiz</span>
        <span class="badge badge-orange">{len(QUIZ_BANK)} savol</span>
    </div>
    <p style="color:{T['text_secondary']};font-size:13px;margin-bottom:16px;">
        Python bilimingizni sinab ko'ring — har safar yangi savol!
    </p>""", unsafe_allow_html=True)

    # Score kartasi
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("✅ To'g'ri", st.session_state.quiz_score)
    sc2.metric("📊 Jami", st.session_state.quiz_total)
    pct = int(st.session_state.quiz_score / st.session_state.quiz_total * 100) if st.session_state.quiz_total else 0
    sc3.metric("🎯 Foiz", f"{pct}%")

    # Progress bar
    if st.session_state.quiz_total > 0:
        st.progress(pct / 100)

    st.divider()

    # Savol yuklash
    if st.session_state.quiz_question is None or (
        st.session_state.quiz_answered and st.button("➡️ Keyingi savol", use_container_width=False)
    ):
        st.session_state.quiz_question = random.choice(QUIZ_BANK)
        st.session_state.quiz_answered = False
        st.rerun()

    if not st.session_state.quiz_answered and st.session_state.quiz_question is None:
        if st.button("🚀 Quizni boshlash", use_container_width=False):
            st.session_state.quiz_question = random.choice(QUIZ_BANK)
            st.rerun()

    q = st.session_state.quiz_question
    if q:
        st.markdown(f'<div class="quiz-card"><h4 style="color:{T["text_primary"]};margin-bottom:16px;">'
                    f'❓ {q["q"]}</h4></div>', unsafe_allow_html=True)

        if not st.session_state.quiz_answered:
            for i, opt in enumerate(q["opts"]):
                if st.button(f"{'ABCD'[i]}) {opt}", key=f"quiz_opt_{i}", use_container_width=True):
                    st.session_state.quiz_total += 1
                    correct = (i == q["ans"])
                    if correct:
                        st.session_state.quiz_score += 1
                        st.success(f"✅ To'g'ri! {q['exp']}")
                    else:
                        st.error(f"❌ Noto'g'ri. To'g'ri javob: **{q['opts'][q['ans']]}**\n\n{q['exp']}")
                    st.session_state.quiz_answered = True
                    st.rerun()
        else:
            correct_opt = q["opts"][q["ans"]]
            st.markdown(f'<div class="card-green" style="color:{T["text_primary"]}">✅ To\'g\'ri javob: <strong>{correct_opt}</strong><br><br>💡 {q["exp"]}</div>',
                        unsafe_allow_html=True)
            st.markdown("")
            if st.button("➡️ Keyingi savol", use_container_width=False, key="next_q_btn"):
                st.session_state.quiz_question = random.choice(QUIZ_BANK)
                st.session_state.quiz_answered  = False
                st.rerun()

    if st.session_state.quiz_total > 0:
        st.divider()
        if st.button("🔄 Scoreni tiklash"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.session_state.quiz_question = None
            st.session_state.quiz_answered  = False
            st.rerun()

# ══════════════════════════════════════════════
# TAB 5 — TARJIMA
# ══════════════════════════════════════════════
with tab_translate:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <span style="font-size:26px;">🌐</span>
        <span style="color:{T['text_primary']};font-size:18px;font-weight:700;">Tarjima</span>
        <span class="badge badge-blue">AI powered</span>
    </div>
    <p style="color:{T['text_secondary']};font-size:13px;margin-bottom:16px;">
        Dasturlash tushunchalari, hujjatlar va kod izohlarini tarjima qiling.
    </p>""", unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1,1])
    with t_col1:
        trans_lang = st.radio("🎯 Tarjima tili:", list(TRANSLATE_PROMPT.keys()), horizontal=True)
    with t_col2:
        trans_mode = st.radio("📋 Rejim:", ["🔤 Matn", "💻 Kod izohi", "📚 Hujjat"], horizontal=True)

    trans_input = st.text_area("📝 Tarjima qilinadigan matn:", height=160,
                               placeholder="Python async/await tushunchasi haqida yozing...")

    if st.button("🌐 Tarjima qilish", use_container_width=False):
        if not trans_input.strip():
            st.warning("⚠️ Matn kiriting!")
        else:
            system = TRANSLATE_PROMPT[trans_lang]
            if "Kod izohi" in trans_mode:
                system += " This is a code comment/documentation, preserve technical terms."
            elif "Hujjat" in trans_mode:
                system += " This is technical documentation, keep formatting and structure."

            with st.spinner(f"🌐 {trans_lang} ga tarjima qilinmoqda..."):
                try:
                    result = simple_ai(trans_input, system, model_choice, temperature=0.3)
                    st.session_state.total_tokens += count_tokens(trans_input + result)
                    log_api_call(count_tokens(trans_input + result))

                    st.markdown(f"**{trans_lang} tarjimasi:**")
                    st.markdown(f'<div class="card-blue" style="color:{T["text_primary"]}">{result}</div>',
                                unsafe_allow_html=True)

                    st.download_button("📥 Saqlash", result,
                        f"translation_{datetime.now().strftime('%H%M')}.txt",
                        "text/plain", use_container_width=False)

                    if st.button("💬 Chat ga yuborish", key="trans_to_chat"):
                        st.session_state.messages.append({
                            "role":"assistant",
                            "content":f"**{trans_lang} tarjima:**\n{result}",
                            "time":fmt_time(),"model":model_choice
                        })
                        st.success("✅ Chat ga yuborildi!")
                except Exception as e:
                    st.error(f"❌ {e}")

    # Tezkor tarjima lug'at
    with st.expander("📖 Python terminlar lug'ati (O'zbek ↔ Ingliz)"):
        terms = {
            "Funksiya":"Function","Sinf":"Class","O'zgaruvchi":"Variable",
            "Ro'yxat":"List","Lug'at":"Dictionary","To'plam":"Set",
            "Qayta ishlash":"Iteration","Rekursiya":"Recursion",
            "Dekorator":"Decorator","Generator":"Generator",
            "Istisno":"Exception","Kutubxona":"Library","Modul":"Module",
            "Ob'ekt":"Object","Meros":"Inheritance","Polimorfizm":"Polymorphism",
        }
        col_uz, col_en = st.columns(2)
        col_uz.markdown("**O'zbekcha**")
        col_en.markdown("**Inglizcha**")
        for uz, en in terms.items():
            col_uz.markdown(f"• {uz}")
            col_en.markdown(f"• {en}")

# ══════════════════════════════════════════════
# TAB 6 — DASHBOARD
# ══════════════════════════════════════════════
with tab_dashboard:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
        <span style="font-size:26px;">📊</span>
        <span style="color:{T['text_primary']};font-size:18px;font-weight:700;">Dashboard</span>
        <span class="badge badge-green">Live</span>
    </div>""", unsafe_allow_html=True)

    # Asosiy metrikalar
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("💬 Xabarlar",    len(st.session_state.messages))
    m2.metric("🔄 Suhbatlar",   st.session_state.conversation_count)
    m3.metric("🪙 Tokenlar",    f"~{st.session_state.total_tokens:,}")
    m4.metric("🏆 Quiz foiz",   f"{pct}%")
    m5.metric("💾 Sessiyalar",  len(st.session_state.saved_sessions))

    st.divider()

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f"#### 📈 Token sarfi (sessiya davomida)")
        calls = st.session_state.dashboard_api_calls
        if calls:
            # Simple bar chart using st.bar_chart
            import pandas as pd
            df = pd.DataFrame(calls)
            df.index = range(1, len(df)+1)
            st.bar_chart(df["tokens"], height=200)
            st.caption(f"Jami {len(calls)} ta API chaqiruv | ~{sum(c['tokens'] for c in calls):,} token")
        else:
            st.info("Hali API chaqiruvlar yo'q. Chat yoki Copilot dan foydalaning.")

    with col_r:
        st.markdown(f"#### 🗂️ Suhbat tarkibi")
        if st.session_state.messages:
            user_msgs = sum(1 for m in st.session_state.messages if m["role"]=="user")
            ai_msgs   = sum(1 for m in st.session_state.messages if m["role"]=="assistant")
            import pandas as pd
            st.bar_chart(pd.DataFrame({
                "Soni": {"👤 Foydalanuvchi": user_msgs, "🐍 AI": ai_msgs}
            }), height=200)
        else:
            st.info("Hali suhbat yo'q.")

    st.divider()

    # Sessiya tarixi
    st.markdown(f"#### 💾 Saqlangan sessiyalar")
    if st.session_state.saved_sessions:
        for i, sess in enumerate(st.session_state.saved_sessions):
            with st.expander(f"📁 {sess['name']} — {sess['date']} ({sess['count']} xabar)"):
                preview = sess["messages"][:2]
                for m in preview:
                    role_icon = "👤" if m["role"]=="user" else "🐍"
                    st.markdown(f"**{role_icon}:** {m['content'][:120]}...")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("📂 Yuklash", key=f"load_{i}"):
                        st.session_state.messages = sess["messages"].copy()
                        st.success(f"✅ '{sess['name']}' yuklandi!")
                        st.rerun()
                with c2:
                    if st.button("🗑️ O'chirish", key=f"del_{i}"):
                        st.session_state.saved_sessions.pop(i)
                        st.rerun()
    else:
        st.info("💾 Sidebar dagi 'Saqlab qo'yish' tugmasidan sessiyalarni saqlang.")

    st.divider()

    # Quiz statistika
    st.markdown("#### 🏆 Quiz statistika")
    if st.session_state.quiz_total > 0:
        qc1, qc2, qc3 = st.columns(3)
        qc1.metric("✅ To'g'ri",  st.session_state.quiz_score)
        qc2.metric("❌ Noto'g'ri", st.session_state.quiz_total - st.session_state.quiz_score)
        qc3.metric("🎯 Daraja",
            "🥇 Expert" if pct>=80 else "🥈 O'rta" if pct>=50 else "🥉 Boshlang'ich")
    else:
        st.info("Quiz hali boshlanmagan. 🏆 Quiz tabiga o'ting!")

    st.divider()
    st.markdown(f'<p style="color:{T["text_secondary"]};font-size:11px;text-align:center">'
                '🐍 AI Python Mentor PRO v4.0 | Jaloliddin | Magistr/Researcher<br>'
                'Powered by Groq + Piston API</p>', unsafe_allow_html=True)
