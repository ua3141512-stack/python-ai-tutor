"""
AI Python Mentor PRO v5.0
Muallif: gulnoza | Magistr/Researcher
Barcha funksiyalar:
  👤 Foydalanuvchi tizimi (nom + shelve DB)
  💬 Chat Mentor (4 rejim, streaming)
  🤖 Copilot (7 amal + diff ko'rsatish)
  🖥️ Code Runner (Piston API)
  🏆 Quiz (10 savol, progress)
  🌐 Tarjima (3 til)
  📊 Dashboard (grafiklar)
  📁 Fayl yuklash (.py .ipynb .txt)
  📤 PDF/HTML eksport
  ✂️ Snippet kutubxonasi
  📈 Progress tracking
  ⚖️ Multi-model solishtirish
  🔗 Kod ulashish
  🐙 GitHub fayl tahlili
  🗓️ Kunlik muammo (Daily Challenge)
"""

import streamlit as st
from groq import Groq
import time, json, shelve, hashlib, requests, difflib, base64, os, re
from datetime import datetime, date
from pathlib import Path
import pandas as pd

# ─────────────────────────────────────
# PATHS
# ─────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH  = str(DATA_DIR / "users")   # shelve faylar shu yerda

# ─────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────
st.set_page_config(
    page_title="AI Python Mentor PRO",
    layout="wide", page_icon="🐍",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI Python Mentor v5.0 | Jaloliddin"}
)

# ─────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("GROQ_API_KEY")
    if not key:
        return None, None
    try:
        return Groq(api_key=key), key
    except:
        return None, None

client, api_key = get_client()

# ─────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────
DEFAULTS = {
    "username": None,
    "messages": [],
    "total_tokens": 0,
    "session_start": datetime.now().strftime("%H:%M"),
    "conversation_count": 0,
    "error_count": 0,
    "copilot_result": "",
    "copilot_before": "",
    "copilot_action_used": "",
    "quick_prompt": None,
    "theme": "dark",
    "saved_sessions": [],
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_question": None,
    "quiz_answered": False,
    "quiz_history": [],
    "dashboard_api_calls": [],
    "runner_output": "",
    "runner_error": "",
    "snippets": [],
    "progress_topics": {},
    "multi_results": {},
    "daily_challenge": None,
    "daily_done": False,
    "shared_codes": {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────
# SHELVE DB  (foydalanuvchi ma'lumotlari)
# ─────────────────────────────────────
def db_get(username: str) -> dict:
    try:
        with shelve.open(DB_PATH) as db:
            return db.get(username, {})
    except:
        return {}

def db_set(username: str, data: dict):
    try:
        with shelve.open(DB_PATH) as db:
            db[username] = data
    except:
        pass

def db_save_session(username: str, name: str, messages: list):
    data = db_get(username)
    sessions = data.get("sessions", [])
    sessions.append({"name": name, "messages": messages,
                     "date": fmt_time(), "count": len(messages)})
    data["sessions"] = sessions[-20:]   # max 20 sessiya
    db_set(username, data)

def db_load_sessions(username: str) -> list:
    return db_get(username).get("sessions", [])

def db_save_progress(username: str, topic: str, score: int):
    data = db_get(username)
    prog = data.get("progress", {})
    prog[topic] = prog.get(topic, 0) + score
    data["progress"] = prog
    db_set(username, data)

def db_load_progress(username: str) -> dict:
    return db_get(username).get("progress", {})

def db_save_snippets(username: str, snippets: list):
    data = db_get(username)
    data["snippets"] = snippets
    db_set(username, data)

def db_load_snippets(username: str) -> list:
    return db_get(username).get("snippets", [])

# ─────────────────────────────────────
# HELPERS
# ─────────────────────────────────────
def fmt_time() -> str:
    return datetime.now().strftime("%H:%M")

def count_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def contains_code(text: str) -> bool:
    return any(k in text for k in ["```","def ","import ","class ","for ","while "])

def export_json() -> str:
    return json.dumps({
        "version": "5.0", "user": st.session_state.username,
        "export_time": datetime.now().isoformat(),
        "messages": st.session_state.messages
    }, ensure_ascii=False, indent=2)

def make_diff_html(old: str, new: str) -> str:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile="Eski kod", tofile="Yangi kod", lineterm=""
    )
    lines = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(f'<span style="color:#3fb950;background:rgba(63,185,80,.1)">{line}</span>')
        elif line.startswith("-") and not line.startswith("---"):
            lines.append(f'<span style="color:#f85149;background:rgba(248,81,73,.1)">{line}</span>')
        elif line.startswith("@@"):
            lines.append(f'<span style="color:#4f9cf9">{line}</span>')
        else:
            lines.append(f'<span style="color:#8b949e">{line}</span>')
    return '<pre style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;overflow-x:auto;font-family:JetBrains Mono,monospace;font-size:12px;line-height:1.6">' + "\n".join(lines) + "</pre>"

def make_short_id(code: str) -> str:
    return hashlib.md5(code.encode()).hexdigest()[:8]

def log_api(tokens: int):
    st.session_state.dashboard_api_calls.append(
        {"time": fmt_time(), "tokens": tokens,
         "ts": datetime.now().timestamp()}
    )

def run_piston(code: str) -> tuple[str, str]:
    try:
        r = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={"language": "python", "version": "3.10.0",
                  "files": [{"name": "main.py", "content": code}]},
            timeout=15
        )
        run = r.json().get("run", {})
        return run.get("stdout", ""), run.get("stderr", "")
    except requests.exceptions.Timeout:
        return "", "⏱️ Timeout (15s)."
    except Exception as e:
        return "", f"❌ {e}"

def fetch_github(url: str) -> str:
    """GitHub URL dan raw kodni olish."""
    raw = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    try:
        r = requests.get(raw, timeout=10)
        if r.status_code == 200:
            return r.text
        return f"❌ HTTP {r.status_code}"
    except Exception as e:
        return f"❌ {e}"

def simple_ai(prompt: str, system: str, model: str, temperature: float = 0.2) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": prompt}],
        stream=False, temperature=temperature, max_tokens=2048,
    )
    return resp.choices[0].message.content

def chat_ai(messages: list, system: str, model: str,
            temperature: float, max_tokens: int, streaming: bool):
    clean = [{"role": m["role"], "content": m["content"]} for m in messages]
    return client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}] + clean,
        stream=streaming, temperature=temperature, max_tokens=max_tokens,
        top_p=0.9, frequency_penalty=0.1, presence_penalty=0.1,
    )

# ─────────────────────────────────────
# TEMA
# ─────────────────────────────────────
IS_DARK = st.session_state.theme == "dark"
T = {
    "bg_p":  "#0d1117" if IS_DARK else "#f6f8fa",
    "bg_s":  "#161b22" if IS_DARK else "#ffffff",
    "bg_c":  "#1c2128" if IS_DARK else "#eef1f4",
    "txt_p": "#e6edf3" if IS_DARK else "#1c2128",
    "txt_s": "#8b949e" if IS_DARK else "#57606a",
    "bdr":   "#30363d" if IS_DARK else "#d0d7de",
    "green": "#00d4aa", "blue": "#4f9cf9",
    "purple":"#bc8cff", "orange":"#f0883e",
}

# ─────────────────────────────────────
# CSS
# ─────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
:root{{
  --bg-p:{T['bg_p']};--bg-s:{T['bg_s']};--bg-c:{T['bg_c']};
  --txt-p:{T['txt_p']};--txt-s:{T['txt_s']};--bdr:{T['bdr']};
  --green:{T['green']};--blue:{T['blue']};--purple:{T['purple']};--orange:{T['orange']};
}}
.stApp{{background:var(--bg-p)!important;font-family:'Inter',sans-serif;color:var(--txt-p)!important}}
h1,h2,h3,h4{{color:var(--txt-p)!important}}
h1{{background:linear-gradient(135deg,var(--green),var(--blue));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700!important}}
/* Tabs */
.stTabs [data-baseweb="tab-list"]{{background:var(--bg-s)!important;border-radius:10px!important;
  padding:4px!important;border:1px solid var(--bdr)!important;gap:3px!important;flex-wrap:wrap!important}}
.stTabs [data-baseweb="tab"]{{color:var(--txt-s)!important;font-weight:500!important;
  border-radius:8px!important;padding:7px 12px!important;font-size:12px!important}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,var(--green),var(--blue))!important;
  color:#000!important;font-weight:700!important}}
/* Chat */
.stChatMessage{{background:var(--bg-s)!important;border:1px solid var(--bdr)!important;
  border-radius:12px!important;margin-bottom:8px!important}}
[data-testid="stChatMessageContent"]{{color:var(--txt-p)!important;
  font-family:'Inter',sans-serif!important;font-size:14px!important;line-height:1.7!important}}
.stChatInputContainer{{background:var(--bg-s)!important;border:1px solid var(--bdr)!important;
  border-radius:12px!important}}
.stChatInputContainer textarea{{color:var(--txt-p)!important;background:transparent!important}}
/* Sidebar */
[data-testid="stSidebar"]{{background:var(--bg-s)!important;border-right:1px solid var(--bdr)!important}}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span{{color:var(--txt-p)!important}}
/* Widgets */
[data-testid="stMetric"]{{background:var(--bg-c)!important;border:1px solid var(--bdr)!important;
  border-radius:8px!important;padding:12px!important}}
[data-testid="stMetricValue"]{{color:var(--txt-p)!important}}
.stSelectbox>div>div,.stMultiSelect>div>div{{background:var(--bg-c)!important;
  border:1px solid var(--bdr)!important;color:var(--txt-p)!important;border-radius:8px!important}}
.stTextArea textarea{{background:var(--bg-c)!important;color:var(--txt-p)!important;
  border:1px solid var(--bdr)!important;border-radius:8px!important;
  font-family:'JetBrains Mono',monospace!important;font-size:13px!important}}
.stTextInput input{{background:var(--bg-c)!important;color:var(--txt-p)!important;
  border:1px solid var(--bdr)!important;border-radius:8px!important}}
/* Buttons */
.stButton>button{{background:linear-gradient(135deg,var(--green),var(--blue))!important;
  color:#000!important;font-weight:600!important;border:none!important;
  border-radius:8px!important;transition:all .2s!important}}
.stButton>button:hover{{transform:translateY(-1px)!important;
  box-shadow:0 4px 20px rgba(0,212,170,.3)!important}}
/* Code */
code{{background:var(--bg-c)!important;color:var(--green)!important;
  font-family:'JetBrains Mono',monospace!important;border-radius:4px!important;padding:2px 6px!important}}
pre{{background:var(--bg-c)!important;border:1px solid var(--bdr)!important;
  border-radius:8px!important;padding:16px!important;font-family:'JetBrains Mono',monospace!important}}
/* Cards */
.card-blue{{border-left:3px solid var(--blue);background:rgba(79,156,249,.05);
  border-radius:10px;padding:16px;color:var(--txt-p)}}
.card-green{{border-left:3px solid var(--green);background:rgba(0,212,170,.05);
  border-radius:10px;padding:16px;color:var(--txt-p)}}
.card-orange{{border-left:3px solid var(--orange);background:rgba(240,136,62,.05);
  border-radius:10px;padding:16px;color:var(--txt-p)}}
.card-purple{{border-left:3px solid var(--purple);background:rgba(188,140,255,.05);
  border-radius:10px;padding:16px;color:var(--txt-p)}}
/* Badges */
.badge{{display:inline-flex;align-items:center;gap:5px;border-radius:20px;
  padding:3px 10px;font-size:11px;font-weight:700;letter-spacing:.5px}}
.b-green{{background:rgba(63,185,80,.1);border:1px solid rgba(63,185,80,.3);color:#3fb950}}
.b-blue{{background:rgba(79,156,249,.1);border:1px solid rgba(79,156,249,.3);color:var(--blue)}}
.b-purple{{background:rgba(188,140,255,.1);border:1px solid rgba(188,140,255,.3);color:var(--purple)}}
.b-orange{{background:rgba(240,136,62,.1);border:1px solid rgba(240,136,62,.3);color:var(--orange)}}
/* Status */
.status{{display:inline-flex;align-items:center;gap:6px;background:rgba(63,185,80,.1);
  border:1px solid rgba(63,185,80,.3);border-radius:20px;padding:4px 12px;
  font-size:12px;color:#3fb950;font-weight:500}}
.dot{{width:6px;height:6px;background:#3fb950;border-radius:50%;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
/* Runner output */
.run-out{{background:#0d1117;border:1px solid var(--bdr);border-radius:8px;padding:16px;
  font-family:'JetBrains Mono',monospace;font-size:13px;color:#00d4aa;
  min-height:60px;white-space:pre-wrap}}
.run-err{{color:#f85149}}
/* Login card */
.login-card{{background:var(--bg-s);border:1px solid var(--bdr);border-radius:16px;
  padding:40px;max-width:440px;margin:60px auto;text-align:center}}
/* Progress bar custom */
.prog-bar{{height:8px;border-radius:4px;background:var(--bdr);margin:4px 0}}
.prog-fill{{height:8px;border-radius:4px;
  background:linear-gradient(90deg,var(--green),var(--blue))}}
/* Mobile */
@media(max-width:768px){{
  .stTabs [data-baseweb="tab"]{{padding:5px 8px!important;font-size:11px!important}}
  h1{{font-size:18px!important}}
}}
hr{{border-color:var(--bdr)!important;margin:14px 0!important}}
::-webkit-scrollbar{{width:6px}}
::-webkit-scrollbar-track{{background:var(--bg-p)}}
::-webkit-scrollbar-thumb{{background:var(--bdr);border-radius:3px}}
</style>
<script>
function playBeep(){{
  try{{
    const c=new AudioContext(),o=c.createOscillator(),g=c.createGain();
    o.connect(g);g.connect(c.destination);
    o.frequency.value=660;o.type='sine';
    g.gain.setValueAtTime(.25,c.currentTime);
    g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.35);
    o.start();o.stop(c.currentTime+.35);
  }}catch(e){{}}
}}
const _obs=new MutationObserver(()=>{{
  const el=document.getElementById('ntfy');
  if(el&&el.dataset.v==='1'){{playBeep();el.dataset.v='0';}}
}});
_obs.observe(document.body,{{subtree:true,attributes:true,childList:true}});
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────
MENTOR_PROMPTS = {
    "Python Mentor 🐍":
        "Sen magistr darajasidagi tajribali Python arxitektisan. Kod tahlili (Big-O, PEP8, SOLID), "
        "xavfsizlik, optimizatsiya va best practices. Javoblaring aniq, kod namunali, O'zbek tilida.",
    "Code Reviewer 🔍":
        "Sen Code Reviewer san. Format: ## 📊 Baho X/10 | ✅ Yaxshi | ⚠️ Kamchilik | "
        "🔧 Yaxshilangan kod | 📈 Complexity. O'zbek tilida.",
    "Debug Ustasi 🐛":
        "Sen Python debug ekspertisan. Format: 🔍 Sabab → 📍 Joy → 🔧 Yechim → 💡 Oldini olish → "
        "✅ Tuzatilgan kod. O'zbek tilida.",
    "Algoritm Muallimi 📚":
        "Sen DSA professor san. Format: Nazariya → ASCII vizual → Python kod → Complexity → Mashq. O'zbek tilida.",
}

COPILOT_PROMPTS = {
    "✨ Yakunlash":   "Faqat Python kodi ber. Tugallanmagan kodni davom ettir. Type hints + docstring. Markdown ``` yo'q.",
    "📖 Tushuntirish":"O'zbek tilida har qatorni izohlash. Complexity qo'sh.",
    "🔧 Tuzatish":    "Xatolarni tuzat. Avval tuzatilgan kod, keyin O'zbek tilida nima o'zgardi.",
    "🧪 Test":        "pytest unit testlar. Edge caseslar. O'zbek tilida qisqa izoh.",
    "🔄 Refactoring": "Kodni qayta yoz: clean code, SOLID, pattern. Avval yangi kod, keyin O'zbek tilida farqlar.",
    "📦 Kutubxona":   "Bu vazifa uchun eng yaxshi Python kutubxonalar. O'zbek tilida: nomi, sababi, pip install, misol.",
    "🔐 Xavfsizlik":  "Kodda xavfsizlik zaifliklarini top. O'zbek tilida: zaiflik turi, xavf darajasi 1-10, tuzatilgan kod.",
}

TRANSLATE_SYS = {
    "🇬🇧 Inglizcha": "Translate to English. Return only the translation.",
    "🇷🇺 Ruscha":    "Переведи на русский. Верни только перевод.",
    "🇺🇿 O'zbekcha": "Translate to Uzbek Latin script. Return only the translation.",
}

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

QUIZ_BANK = [
    {"q":"Python'da `is` va `==` farqi?",
     "opts":["Ikkalasi bir xil","is — ob'ekt ID, == — qiymat tengligini tekshiradi",
             "== — ob'ekt ID, is — qiymatni","Faqat son uchun"],"ans":1,
     "exp":"`is` id() solishtiradi, `==` qiymat solishtiradi.","topic":"Asoslar"},
    {"q":"Python GIL nima?",
     "opts":["Global Import Lock","Global Interpreter Lock","General Input Library","None"],"ans":1,
     "exp":"GIL — bir vaqtda faqat bitta thread bytekod bajara oladi.","topic":"Parallellik"},
    {"q":"`*args` va `**kwargs` farqi?",
     "opts":["Farqi yo'q","*args — ro'yxat, **kwargs — lug'at",
             "*args — positional tuple, **kwargs — keyword dict","Faqat classlarda"],"ans":2,
     "exp":"*args → tuple, **kwargs → dict.","topic":"Funksiyalar"},
    {"q":"List comprehension vs for loop — qaysi tezroq?",
     "opts":["For loop","List comprehension","Teng","Faqat kichik listda"],"ans":1,
     "exp":"List comprehension C darajasida optimalashtirilgan, ~35-50% tezroq.","topic":"Optimizatsiya"},
    {"q":"`__slots__` nima uchun?",
     "opts":["Magic method","Xotira tejash — __dict__ o'rniga","Import tezlatish","Faqat dataclass"],"ans":1,
     "exp":"__slots__ atributlarni static arrayda saqlaydi, 40-50% kam xotira.","topic":"OOP"},
    {"q":"`@staticmethod` va `@classmethod` farqi?",
     "opts":["Farqi yo'q","@staticmethod — na self na cls; @classmethod — cls oladi",
             "@classmethod — na self na cls","Ikkalasi self oladi"],"ans":1,
     "exp":"@staticmethod hech narsa olmaydi, @classmethod cls oladi.","topic":"OOP"},
    {"q":"`deepcopy` va `copy` farqi?",
     "opts":["Farqi yo'q","deepcopy — ichki ob'ektlarni ham nusxalaydi",
             "copy — ichki nusxalaydi","Faqat list uchun"],"ans":1,
     "exp":"copy — shallow, deepcopy — recursive deep nusxa.","topic":"Xotira"},
    {"q":"Generator vs List — xotira?",
     "opts":["Farqi yo'q","Generator lazy, xotira tejaydi","List lazy","Generator ko'proq xotira"],"ans":1,
     "exp":"1M element: list ~8MB, generator ~120 byte.","topic":"Optimizatsiya"},
    {"q":"`with` statement nima uchun?",
     "opts":["Faqat fayl","Context manager — resursni avtomatik yopish","try/except o'rnida","Import"],"ans":1,
     "exp":"__enter__ va __exit__ chaqiradi, resursni xavfsiz boshqaradi.","topic":"Asoslar"},
    {"q":"Python'da `@property` nima?",
     "opts":["Oddiy decorator","Metodni attribute kabi chaqirish imkonini beradi",
             "Class o'zgaruvchisi","Abstract method"],"ans":1,
     "exp":"@property getter/setter/deleter ni clean sintaksis bilan aniqlaydi.","topic":"OOP"},
    {"q":"`asyncio` qanday ishlaydi?",
     "opts":["Ko'p thread","Ko'p process","Event loop — bitta thread, cooperative multitasking","GIL bilan"],"ans":2,
     "exp":"asyncio bitta thread da event loop orqali I/O-bound vazifalarni parallel bajaradi.","topic":"Parallellik"},
    {"q":"Python `dict` qaysi data strukturasiga asoslanadi?",
     "opts":["Binary tree","Linked list","Hash table","Array"],"ans":2,
     "exp":"dict — hash table, O(1) average lookup/insert/delete.","topic":"Data Strukturalar"},
]

BUILTIN_SNIPPETS = [
    {"name":"Singleton Pattern","tag":"OOP","code":
"""class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance"""},
    {"name":"Context Manager","tag":"Advanced","code":
"""from contextlib import contextmanager

@contextmanager
def managed_resource(name: str):
    print(f\"Opening: {name}\")
    try:
        yield name
    finally:
        print(f\"Closing: {name}\")"""},
    {"name":"Decorator with args","tag":"Advanced","code":
"""import functools

def retry(times: int = 3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times - 1:
                        raise
            return None
        return wrapper
    return decorator"""},
    {"name":"Dataclass Example","tag":"OOP","code":
"""from dataclasses import dataclass, field
from typing import List

@dataclass
class Student:
    name: str
    age: int
    grades: List[float] = field(default_factory=list)

    @property
    def average(self) -> float:
        return sum(self.grades) / len(self.grades) if self.grades else 0.0"""},
    {"name":"Async HTTP Request","tag":"Async","code":
"""import asyncio
import aiohttp

async def fetch(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    data = await fetch(\"https://api.example.com/data\")
    print(data)

asyncio.run(main())"""},
    {"name":"Binary Search","tag":"Algoritm","code":
"""def binary_search(arr: list, target: int) -> int:
    \"\"\"O(log n) qidiruv. Sorted array kerak.\"\"\"
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""},
    {"name":"LRU Cache","tag":"Optimizatsiya","code":
"""from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    \"\"\"Memoized Fibonacci — O(n) vaqt, O(n) xotira.\"\"\"
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)"""},
]

DAILY_CHALLENGES = [
    {"title":"FizzBuzz Pro","difficulty":"🟢 Oson",
     "desc":"1 dan 100 gacha: 3 ga bo'linsa 'Fizz', 5 ga bo'linsa 'Buzz', ikkalasiga bo'linsa 'FizzBuzz' chiqaring. List comprehension bilan yozing.",
     "hint":"[... for i in range(1,101)]","topic":"Asoslar"},
    {"title":"Palindrome tekshirish","difficulty":"🟡 O'rta",
     "desc":"So'z yoki jumla palindrome ekanligini tekshiruvchi funksiya yozing. Bo'shliq va katta-kichik harflarni e'tiborsiz qoldiring.",
     "hint":"s.lower().replace(' ','')","topic":"Stringlar"},
    {"title":"Flat Nested List","difficulty":"🟡 O'rta",
     "desc":"Ixtiyoriy darajadagi ichma-ich ro'yxatni tekis qilib chiqaradigan generator yozing. [[1,[2,3]],[4]] → [1,2,3,4]",
     "hint":"yield from","topic":"Generatorlar"},
    {"title":"LRU Cache from scratch","difficulty":"🔴 Qiyin",
     "desc":"OrderedDict yoki doubly linked list + dict bilan O(1) get/put LRU Cache class yozing.",
     "hint":"collections.OrderedDict","topic":"Data Strukturalar"},
    {"title":"Async Downloader","difficulty":"🔴 Qiyin",
     "desc":"asyncio + aiohttp bilan bir vaqtda 5 ta URL dan ma'lumot yuklovchi funksiya yozing. Natijalarni tuple list sifatida qaytaring.",
     "hint":"asyncio.gather(*tasks)","topic":"Async"},
    {"title":"Decorator chain","difficulty":"🟡 O'rta",
     "desc":"@timer va @logger decoratorlarini yozing. @timer funksiya vaqtini o'lchaydi, @logger kirish/chiqish qiymatlarini chiqaradi.",
     "hint":"functools.wraps","topic":"Dekoratorlar"},
    {"title":"Custom Iterator","difficulty":"🟡 O'rta",
     "desc":"Fibonacci sonlarini chiqaruvchi iterator class yozing. __iter__ va __next__ methodlarini implement qiling.",
     "hint":"StopIteration","topic":"OOP"},
]

# ─────────────────────────────────────
# LOGIN EKRANI
# ─────────────────────────────────────
if not st.session_state.username:
    st.markdown(f"""
    <div class="login-card">
      <div style="font-size:56px;margin-bottom:8px">🐍</div>
      <h2 style="color:{T['txt_p']};margin-bottom:4px">AI Python Mentor PRO</h2>
      <p style="color:{T['txt_s']};font-size:14px;margin-bottom:28px">v5.0 — Magistratura darajasidagi yordamchi</p>
    </div>
    """, unsafe_allow_html=True)

    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        uname = st.text_input("👤 Ismingizni kiriting:", placeholder="Masalan: Jaloliddin",
                               max_chars=30)
        if st.button("🚀 Kirish", use_container_width=True):
            if uname.strip():
                uname = uname.strip()
                st.session_state.username = uname
                # DB dan oldingi ma'lumotlarni yuklash
                st.session_state.snippets       = db_load_snippets(uname) or BUILTIN_SNIPPETS.copy()
                st.session_state.saved_sessions = db_load_sessions(uname)
                st.session_state.progress_topics= db_load_progress(uname)
                st.success(f"✅ Xush kelibsiz, {uname}!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("⚠️ Ism kiriting!")
    st.stop()

# ─────────────────────────────────────
# HEADER
# ─────────────────────────────────────
h1, h2, h3, h4 = st.columns([3, 1, 0.8, 0.8])
with h1:
    st.title("🐍 AI Python Mentor PRO")
    st.caption(f"v5.0 | 👤 {st.session_state.username} | {st.session_state.session_start} da boshlangan")
with h2:
    if st.button("🌙 Dark" if not IS_DARK else "☀️ Light", use_container_width=True):
        st.session_state.theme = "light" if IS_DARK else "dark"
        st.rerun()
with h3:
    if api_key:
        st.markdown('<div class="status"><span class="dot"></span>Online</div>',
                    unsafe_allow_html=True)
    else:
        st.error("Offline")
with h4:
    if st.button("🚪 Chiqish", use_container_width=True):
        st.session_state.username = None
        st.rerun()
st.divider()

# ─────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    mentor_mode   = st.selectbox("🎯 Mentor rejimi", list(MENTOR_PROMPTS.keys()))
    model_choice  = st.selectbox("🤖 Model", MODELS)
    temperature   = st.slider("🌡️ Ijodkorlik", 0.0, 1.0, 0.7, 0.1)
    max_tokens    = st.select_slider("📏 Javob uzunligi", [512,1024,2048,4096,8192], value=2048)
    max_history   = st.slider("💬 Tariх uzunligi", 2, 30, 10, 2)
    use_streaming = st.toggle("⚡ Streaming", value=True)
    notify_sound  = st.toggle("🔔 Ovozli xabar", value=True)
    st.divider()

    st.markdown("### 📊 Statistika")
    c1, c2 = st.columns(2)
    c1.metric("💬", len(st.session_state.messages))
    c2.metric("🔄", st.session_state.conversation_count)
    st.metric("🪙 Token", f"~{st.session_state.total_tokens:,}")
    quiz_pct = int(st.session_state.quiz_score/st.session_state.quiz_total*100) if st.session_state.quiz_total else 0
    st.metric("🏆 gulnoza", f"{st.session_state.quiz_score}/{st.session_state.quiz_total} ({quiz_pct}%)")
    st.divider()

    st.markdown("### 💾 Sessiya")
    sname = st.text_input("Sessiya nomi:", placeholder="Mening suhbatim")
    if st.button("💾 Saqlash", use_container_width=True):
        if st.session_state.messages:
            n = sname or f"Sessiya {fmt_time()}"
            db_save_session(st.session_state.username, n, st.session_state.messages)
            st.session_state.saved_sessions = db_load_sessions(st.session_state.username)
            st.success(f"✅ '{n}' saqlandi!")
        else:
            st.warning("Suhbat bo'sh!")

    if st.session_state.saved_sessions:
        names = [s["name"] for s in st.session_state.saved_sessions]
        sel = st.selectbox("📂 Yuklash:", ["— tanlang —"] + names)
        if sel != "— tanlang —" and st.button("📂 Yuklash", use_container_width=True):
            found = next((x for x in st.session_state.saved_sessions if x["name"]==sel), None)
            if found:
                st.session_state.messages = found["messages"].copy()
                st.success(f"✅ '{sel}' yuklandi!")
                st.rerun()
    st.divider()

    if st.button("🗑️ Suhbatni tozalash", use_container_width=True):
        for k in ["messages","copilot_result","copilot_before","runner_output","runner_error","multi_results"]:
            st.session_state[k] = [] if k=="messages" else ({} if k=="multi_results" else "")
        st.session_state.total_tokens = 0
        st.session_state.conversation_count = 0
        st.success("✅ Tozalandi!")
        time.sleep(0.3); st.rerun()

    if st.session_state.messages:
        st.download_button("📥 JSON eksport", export_json(),
            f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            "application/json", use_container_width=True)
    st.divider()

    st.markdown("### 💡 Tezkor savollar")
    for q in ["list vs tuple?","GIL nima?","Decorator?","async/await?","Generator?"]:
        if st.button(q, use_container_width=True, key=f"sq_{q}"):
            st.session_state.quick_prompt = q; st.rerun()

    st.divider()
    st.markdown(f'<p style="color:{T["txt_s"]};font-size:11px;text-align:center">'
                '🐍 v5.0 PRO | Jaloliddin<br>Magistr/Researcher<br>'
                'Groq + Piston API</p>', unsafe_allow_html=True)

# ─────────────────────────────────────
# API KEY CHECK
# ─────────────────────────────────────
if not api_key:
    st.warning("⚠️ `GROQ_API_KEY` ni `.streamlit/secrets.toml` ga qo'shing.")
    st.code('GROQ_API_KEY = "gsk_your_key_here"', language="toml")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
TABS = ["💬 Chat","🤖 Copilot","🖥️ Runner","🏆 Quiz",
        "🌐 Tarjima","✂️ Snippets","📈 Progress",
        "⚖️ Multi-Model","🔗 Share","🐙 GitHub","🗓️ Challenge","📊 Dashboard"]

(tab_chat, tab_copilot, tab_runner, tab_quiz, tab_trans,
 tab_snip, tab_prog, tab_multi, tab_share,
 tab_github, tab_challenge, tab_dash) = st.tabs(TABS)

# ══════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════
with tab_chat:
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="text-align:center;padding:36px 20px">
          <h2 style="color:{T['txt_p']};font-size:22px">Salom, {st.session_state.username}! 👋</h2>
          <p style="color:{T['txt_s']};font-size:14px;max-width:520px;margin:0 auto 20px">
            Python haqida istalgan savol bering yoki 11 ta tabdan birini ishlating.
          </p>
          <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
            {''.join(f'<span style="background:{T["bg_c"]};border:1px solid {T["bdr"]};border-radius:8px;padding:6px 12px;font-size:12px;color:{T["txt_p"]}">{x}</span>'
                     for x in ["🔍 Tahlil","🐛 Debug","📚 Algoritm","⚡ Optim","🔐 Xavfsizlik"])}
          </div>
        </div>""", unsafe_allow_html=True)

    # Fayl yuklash (chat ichida)
    with st.expander("📁 Fayl yuklash (.py .ipynb .txt .md)"):
        uploaded = st.file_uploader("Fayl tanlang:", type=["py","txt","md","ipynb"],
                                     label_visibility="collapsed")
        if uploaded:
            raw = uploaded.read().decode("utf-8", errors="ignore")
            if uploaded.name.endswith(".ipynb"):
                try:
                    nb = json.loads(raw)
                    cells = nb.get("cells", [])
                    code_cells = ["\n".join(c["source"]) for c in cells if c["cell_type"]=="code"]
                    raw = "\n\n# --- cell ---\n\n".join(code_cells)
                except:
                    pass
            preview = raw[:200] + ("..." if len(raw)>200 else "")
            st.code(preview, language="python")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📊 Tahlil qil", key="file_analyze"):
                    st.session_state.quick_prompt = f"Quyidagi kodni tahlil qil:\n```python\n{raw[:4000]}\n```"
                    st.rerun()
            with col_b:
                if st.button("🔐 Xavfsizlik skaner", key="file_sec"):
                    st.session_state.quick_prompt = f"Quyidagi kodda xavfsizlik zaifliklarini top:\n```python\n{raw[:4000]}\n```"
                    st.rerun()

    # Xabarlarni ko'rsatish
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🐍"):
            st.markdown(msg["content"])
            if "time" in msg:
                st.caption(f"🕐 {msg['time']}")

    prompt = st.session_state.get("quick_prompt")
    if prompt:
        st.session_state.quick_prompt = None
    inp = st.chat_input("Savol bering, kod tashlang yoki xato yuboring...")
    if inp:
        prompt = inp

    if prompt:
        t = fmt_time()
        st.session_state.messages.append({"role":"user","content":prompt,"time":t})
        st.session_state.total_tokens += count_tokens(prompt)

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt); st.caption(f"🕐 {t}")

        with st.chat_message("assistant", avatar="🐍"):
            ph = st.empty(); full = ""; rt = fmt_time()
            try:
                recent = st.session_state.messages[-max_history:]
                if contains_code(prompt):
                    ph.markdown("*🔍 Tahlil qilinmoqda...*")
                comp = chat_ai(recent, MENTOR_PROMPTS[mentor_mode],
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
                st.session_state.messages.append({"role":"assistant","content":full,"time":rt})
                st.session_state.total_tokens += count_tokens(full)
                st.session_state.conversation_count += 1
                log_api(count_tokens(prompt+full))
                st.session_state.error_count = 0
                if notify_sound:
                    st.markdown('<div id="ntfy" data-v="1"></div>', unsafe_allow_html=True)
            except Exception as e:
                err=str(e)
                st.session_state.error_count+=1
                if "rate_limit" in err.lower():   st.error("⏱️ Rate limit — 30s kuting.")
                elif "api_key"  in err.lower():   st.error("🔑 API kalit noto'g'ri.")
                elif "model_not"in err.lower():   st.error(f"🤖 Model topilmadi: `{model_choice}`")
                elif "context"  in err.lower():   st.error("📏 Kontekst oshdi — tozalang.")
                else:                              st.error(f"❌ {err}")

# ══════════════════════════════════════════════
# TAB 2 — COPILOT
# ══════════════════════════════════════════════
with tab_copilot:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🤖</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">AI Copilot</span>'
                f'<span class="badge b-purple">7 amal</span></div>', unsafe_allow_html=True)

    cop_action = st.radio("🎯 Amal:", list(COPILOT_PROMPTS.keys()), horizontal=True)
    hints = {"✨ Yakunlash":"Tugallanmagan kod → to'liq implementatsiya + type hints + docstring",
             "📖 Tushuntirish":"Har qator O'zbek tilida izoh + Big-O",
             "🔧 Tuzatish":"Xatolarni tuzatish + diff ko'rsatish",
             "🧪 Test":"pytest unit testlar + edge cases",
             "🔄 Refactoring":"Clean code + SOLID + diff ko'rsatish",
             "📦 Kutubxona":"Eng yaxshi lib tavsiyalar + pip + misol",
             "🔐 Xavfsizlik":"OWASP scan + xavf darajasi + tuzatilgan kod"}
    st.caption(hints.get(cop_action,""))

    code_in = st.text_area("📝 Kodingizni kiriting:", height=220,
                            placeholder="def fibonacci(n):\n    # davom ettiring...")
    c1,c2,c3 = st.columns([2,1,1])
    with c1: run_cop = st.button("🚀 Ishlatish", use_container_width=True)
    with c2: clr_cop = st.button("🗑️ Tozalash", use_container_width=True, key="cop_clr")
    with c3:
        if st.session_state.copilot_result:
            ext = ".txt" if "Tushuntirish" in st.session_state.copilot_action_used else ".py"
            st.download_button("💾 Saqlash", st.session_state.copilot_result,
                f"copilot{ext}", "text/plain", use_container_width=True)

    if clr_cop:
        st.session_state.copilot_result = ""
        st.session_state.copilot_before = ""
        st.rerun()

    if run_cop:
        if not code_in.strip():
            st.warning("⚠️ Kod kiriting!")
        else:
            spinner_map = {"✨ Yakunlash":"⚡ Yakunlanmoqda...","📖 Tushuntirish":"📖 Tahlil...",
                           "🔧 Tuzatish":"🔧 Tuzatilmoqda...","🧪 Test":"🧪 Test yozilmoqda...",
                           "🔄 Refactoring":"🔄 Refactoring...","📦 Kutubxona":"📦 Kutubxonalar...",
                           "🔐 Xavfsizlik":"🔐 Skanerlash..."}
            with st.spinner(spinner_map.get(cop_action,"⚙️...")):
                try:
                    result = simple_ai(code_in, COPILOT_PROMPTS[cop_action], model_choice)
                    st.session_state.copilot_result     = result
                    st.session_state.copilot_before     = code_in
                    st.session_state.copilot_action_used = cop_action
                    st.session_state.total_tokens += count_tokens(code_in+result)
                    log_api(count_tokens(code_in+result))
                except Exception as e:
                    st.error(f"❌ {e}")

    if st.session_state.copilot_result:
        st.divider()
        used = st.session_state.copilot_action_used
        st.markdown(f"**{used} natijasi:**")

        # Diff ko'rsatish (Tuzatish va Refactoring uchun)
        show_diff = used in ("🔧 Tuzatish","🔄 Refactoring") and st.session_state.copilot_before
        if show_diff:
            view_mode = st.radio("👁️ Ko'rinish:", ["✨ Yangi kod","🔀 Diff (before/after)"], horizontal=True)
            if view_mode == "🔀 Diff (before/after)":
                st.markdown(make_diff_html(
                    st.session_state.copilot_before,
                    st.session_state.copilot_result
                ), unsafe_allow_html=True)
            else:
                st.code(st.session_state.copilot_result, language="python")
        elif used in ("📖 Tushuntirish","📦 Kutubxona","🔐 Xavfsizlik"):
            card = {"📖 Tushuntirish":"card-green","📦 Kutubxona":"card-blue","🔐 Xavfsizlik":"card-orange"}
            cls  = card.get(used,"card-blue")
            st.markdown(f'<div class="{cls}">{st.session_state.copilot_result}</div>',
                        unsafe_allow_html=True)
        else:
            st.code(st.session_state.copilot_result, language="python")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("💬 Chat ga yuborish"):
                is_code = "Tushuntirish" not in used
                content = (f"**Copilot ({used}):**\n```python\n{st.session_state.copilot_result}\n```"
                           if is_code else
                           f"**Copilot tushuntirishi:**\n{st.session_state.copilot_result}")
                st.session_state.messages.append({"role":"assistant","content":content,"time":fmt_time()})
                st.success("✅ Chat ga yuborildi!")
        with col_b:
            if st.button("▶️ Runner ga yuborish"):
                st.session_state["runner_prefill"] = st.session_state.copilot_result
                st.success("✅ Runner ga yuborildi!")
        with col_c:
            if "Tuzatish" not in used and "Tushuntirish" not in used:
                if st.button("✂️ Snippet saqlash"):
                    new_s = {"name":f"Copilot — {fmt_time()}",
                             "tag":"Copilot","code":st.session_state.copilot_result}
                    st.session_state.snippets.append(new_s)
                    db_save_snippets(st.session_state.username, st.session_state.snippets)
                    st.success("✅ Snippet saqlandi!")

# ══════════════════════════════════════════════
# TAB 3 — CODE RUNNER
# ══════════════════════════════════════════════
with tab_runner:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🖥️</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Code Runner</span>'
                f'<span class="badge b-green">Python 3.10</span></div>', unsafe_allow_html=True)

    prefill = st.session_state.pop("runner_prefill", None)
    default_code = prefill if prefill else \
        '# Misol:\nfor i in range(1, 8):\n    stars = "★" * i\n    print(f"{i}: {stars}")\nprint("\\nTayyor! ✅")'

    runner_code = st.text_area("📝 Python kodi:", value=default_code, height=260, key="runner_in")

    c1,c2,c3,c4 = st.columns([2,1,1,1])
    with c1: run_btn  = st.button("▶️ Bajarish", use_container_width=True)
    with c2: clr_btn  = st.button("🗑️ Tozalash", use_container_width=True, key="run_clr")
    with c3: cop_btn  = st.button("🤖 Copilot", use_container_width=True, key="run_cop")
    with c4: snip_btn = st.button("✂️ Snippet", use_container_width=True, key="run_snip")

    if clr_btn:
        st.session_state.runner_output = ""
        st.session_state.runner_error  = ""
        st.rerun()
    if cop_btn:
        st.session_state["copilot_prefill"] = runner_code
        st.info("Copilot tabiga o'ting!")
    if snip_btn and runner_code.strip():
        st.session_state.snippets.append({"name":f"Runner — {fmt_time()}","tag":"Runner","code":runner_code})
        db_save_snippets(st.session_state.username, st.session_state.snippets)
        st.success("✅ Snippet saqlandi!")

    if run_btn and runner_code.strip():
        with st.spinner("⚙️ Bajarilmoqda..."):
            out, err = run_piston(runner_code)
            st.session_state.runner_output = out
            st.session_state.runner_error  = err

    if st.session_state.runner_output or st.session_state.runner_error:
        st.markdown("**📤 Natija:**")
        if st.session_state.runner_output:
            st.markdown(f'<div class="run-out">{st.session_state.runner_output}</div>',
                        unsafe_allow_html=True)
        if st.session_state.runner_error:
            st.markdown(f'<div class="run-out run-err">⚠️ Xatolik:\n{st.session_state.runner_error}</div>',
                        unsafe_allow_html=True)
            if st.button("🔧 Xatoni Copilot bilan tuzatish"):
                with st.spinner("🔧 Tuzatilmoqda..."):
                    try:
                        fixed = simple_ai(
                            f"Kod:\n{runner_code}\n\nXatolik:\n{st.session_state.runner_error}",
                            COPILOT_PROMPTS["🔧 Tuzatish"], model_choice
                        )
                        st.session_state.copilot_result = fixed
                        st.session_state.copilot_before = runner_code
                        st.session_state.copilot_action_used = "🔧 Tuzatish"
                        st.success("✅ Copilot tabiga o'ting!")
                    except Exception as e:
                        st.error(f"❌ {e}")

    st.caption("ℹ️ Piston API: Python 3.10 • Max 15s • stdin yo'q")

# ══════════════════════════════════════════════
# TAB 4 — QUIZ
# ══════════════════════════════════════════════
with tab_quiz:
    import random as _rnd
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🏆</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Python Quiz</span>'
                f'<span class="badge b-orange">{len(QUIZ_BANK)} savol</span></div>',
                unsafe_allow_html=True)

    q1,q2,q3 = st.columns(3)
    q1.metric("✅ To'g'ri", st.session_state.quiz_score)
    q2.metric("📊 Jami",    st.session_state.quiz_total)
    q3.metric("🎯 Foiz",    f"{quiz_pct}%")
    if st.session_state.quiz_total:
        st.progress(quiz_pct/100)
    st.divider()

    # Mavzu filtri
    topics = list({q["topic"] for q in QUIZ_BANK})
    sel_topic = st.selectbox("📂 Mavzu:", ["Hammasi"] + sorted(topics))
    filtered = QUIZ_BANK if sel_topic=="Hammasi" else [q for q in QUIZ_BANK if q["topic"]==sel_topic]

    if st.session_state.quiz_question is None:
        if st.button("🚀 Quizni boshlash", use_container_width=False):
            st.session_state.quiz_question = _rnd.choice(filtered)
            st.session_state.quiz_answered  = False
            st.rerun()

    q = st.session_state.quiz_question
    if q:
        st.markdown(f'<div style="background:{T["bg_s"]};border:1px solid {T["bdr"]};'
                    f'border-radius:14px;padding:20px">'
                    f'<span class="badge b-blue" style="margin-bottom:10px;display:inline-block">'
                    f'{q["topic"]}</span>'
                    f'<h4 style="color:{T["txt_p"]};margin:8px 0 16px">❓ {q["q"]}</h4>'
                    f'</div>', unsafe_allow_html=True)

        if not st.session_state.quiz_answered:
            for i, opt in enumerate(q["opts"]):
                if st.button(f"{'ABCD'[i]}) {opt}", key=f"qo_{i}", use_container_width=True):
                    st.session_state.quiz_total += 1
                    correct = (i == q["ans"])
                    if correct:
                        st.session_state.quiz_score += 1
                        db_save_progress(st.session_state.username, q["topic"], 1)
                        st.session_state.progress_topics = db_load_progress(st.session_state.username)
                        st.success(f"✅ To'g'ri! {q['exp']}")
                    else:
                        st.error(f"❌ Noto'g'ri. To'g'ri: **{q['opts'][q['ans']]}**\n\n{q['exp']}")
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_history.append({
                        "q":q["q"],"correct":correct,"topic":q["topic"],"time":fmt_time()})
                    st.rerun()
        else:
            st.markdown(f'<div class="card-green">✅ To\'g\'ri javob: <strong>{q["opts"][q["ans"]]}</strong>'
                        f'<br><br>💡 {q["exp"]}</div>', unsafe_allow_html=True)
            st.markdown("")
            if st.button("➡️ Keyingi savol", use_container_width=False):
                st.session_state.quiz_question = _rnd.choice(filtered)
                st.session_state.quiz_answered  = False
                st.rerun()

    if st.session_state.quiz_total:
        st.divider()
        if st.button("🔄 Scoreni tiklash"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.session_state.quiz_question = None
            st.session_state.quiz_history  = []
            st.rerun()

        if st.session_state.quiz_history:
            with st.expander("📜 Quiz tarixi"):
                for h in reversed(st.session_state.quiz_history[-10:]):
                    icon = "✅" if h["correct"] else "❌"
                    st.markdown(f"{icon} **{h['topic']}** — {h['q'][:60]}... `{h['time']}`")

# ══════════════════════════════════════════════
# TAB 5 — TARJIMA
# ══════════════════════════════════════════════
with tab_trans:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🌐</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Tarjima</span>'
                f'<span class="badge b-blue">3 til</span></div>', unsafe_allow_html=True)

    tr1,tr2 = st.columns(2)
    with tr1: trans_lang = st.radio("🎯 Til:", list(TRANSLATE_SYS.keys()), horizontal=True)
    with tr2: trans_mode = st.radio("📋 Rejim:", ["🔤 Matn","💻 Kod izohi","📚 Hujjat"], horizontal=True)

    trans_in = st.text_area("📝 Matn kiriting:", height=160,
                             placeholder="Python async/await haqida...")

    if st.button("🌐 Tarjima qilish", use_container_width=False):
        if not trans_in.strip():
            st.warning("⚠️ Matn kiriting!")
        else:
            sys = TRANSLATE_SYS[trans_lang]
            if "Kod" in trans_mode:   sys += " Preserve technical terms."
            elif "Hujjat" in trans_mode: sys += " Keep formatting."
            with st.spinner(f"🌐 {trans_lang} ga tarjima..."):
                try:
                    result = simple_ai(trans_in, sys, model_choice, 0.3)
                    st.session_state.total_tokens += count_tokens(trans_in+result)
                    st.markdown(f"**{trans_lang} tarjimasi:**")
                    st.markdown(f'<div class="card-blue">{result}</div>', unsafe_allow_html=True)
                    st.download_button("📥 Saqlash", result,
                        f"trans_{datetime.now().strftime('%H%M')}.txt","text/plain")
                except Exception as e:
                    st.error(f"❌ {e}")

    with st.expander("📖 Python terminlar lug'ati"):
        terms = {"Funksiya":"Function","Sinf":"Class","O'zgaruvchi":"Variable",
                 "Ro'yxat":"List","Lug'at":"Dictionary","Rekursiya":"Recursion",
                 "Dekorator":"Decorator","Generator":"Generator","Istisno":"Exception",
                 "Ob'ekt":"Object","Meros":"Inheritance","Polimorfizm":"Polymorphism",
                 "Inkapsulyatsiya":"Encapsulation","Abstraksiya":"Abstraction"}
        t1,t2 = st.columns(2)
        t1.markdown("**O'zbekcha**"); t2.markdown("**Inglizcha**")
        for uz,en in terms.items():
            t1.markdown(f"• {uz}"); t2.markdown(f"• {en}")

# ══════════════════════════════════════════════
# TAB 6 — SNIPPETS
# ══════════════════════════════════════════════
with tab_snip:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">✂️</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Snippet Kutubxonasi</span>'
                f'<span class="badge b-green">{len(st.session_state.snippets)} ta</span></div>',
                unsafe_allow_html=True)

    # Yangi snippet qo'shish
    with st.expander("➕ Yangi snippet qo'shish"):
        sn1,sn2 = st.columns(2)
        with sn1: new_name = st.text_input("Nomi:", key="snip_name")
        with sn2: new_tag  = st.text_input("Tag:", placeholder="OOP, Algoritm...", key="snip_tag")
        new_code = st.text_area("Kodi:", height=150, key="snip_code")
        if st.button("💾 Qo'shish", use_container_width=False, key="snip_add"):
            if new_name and new_code:
                st.session_state.snippets.append(
                    {"name":new_name,"tag":new_tag or "General","code":new_code})
                db_save_snippets(st.session_state.username, st.session_state.snippets)
                st.success("✅ Saqlandi!"); st.rerun()

    # Filtrlash
    all_tags = list({s.get("tag","General") for s in st.session_state.snippets})
    sel_tag  = st.selectbox("🏷️ Tag bo'yicha filtr:", ["Hammasi"] + sorted(all_tags))
    search   = st.text_input("🔍 Qidirish:", placeholder="decorator...")

    shown = [s for s in st.session_state.snippets
             if (sel_tag=="Hammasi" or s.get("tag")==sel_tag)
             and (not search or search.lower() in s["name"].lower() or search.lower() in s["code"].lower())]

    if not shown:
        st.info("Snippet topilmadi.")
    else:
        for i, snip in enumerate(shown):
            real_i = st.session_state.snippets.index(snip)
            with st.expander(f"✂️ {snip['name']}  `{snip.get('tag','')}`"):
                st.code(snip["code"], language="python")
                sc1,sc2,sc3,sc4 = st.columns(4)
                with sc1:
                    if st.button("▶️ Runner", key=f"snip_run_{real_i}"):
                        st.session_state["runner_prefill"] = snip["code"]
                        st.info("Runner tabiga o'ting!")
                with sc2:
                    if st.button("🤖 Copilot", key=f"snip_cop_{real_i}"):
                        st.session_state.quick_prompt = f"Quyidagi kodni tahlil qil:\n```python\n{snip['code']}\n```"
                        st.info("Chat tabiga o'ting!")
                with sc3:
                    if st.button("📋 Chat ga", key=f"snip_chat_{real_i}"):
                        st.session_state.messages.append({
                            "role":"user",
                            "content":f"```python\n{snip['code']}\n```",
                            "time":fmt_time()})
                        st.success("✅ Chat ga yuborildi!")
                with sc4:
                    if st.button("🗑️ O'chirish", key=f"snip_del_{real_i}"):
                        st.session_state.snippets.pop(real_i)
                        db_save_snippets(st.session_state.username, st.session_state.snippets)
                        st.rerun()

# ══════════════════════════════════════════════
# TAB 7 — PROGRESS
# ══════════════════════════════════════════════
with tab_prog:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">📈</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Progress Tracking</span>'
                f'</div>', unsafe_allow_html=True)

    prog = st.session_state.progress_topics
    all_topics = list({q["topic"] for q in QUIZ_BANK})

    if not prog:
        st.info("📊 Hali progress yo'q. Quiz ni ishlating!")
    else:
        # Grafik
        prog_df = pd.DataFrame([
            {"Mavzu": t, "To'g'ri javoblar": prog.get(t,0)}
            for t in all_topics
        ]).sort_values("To'g'ri javoblar", ascending=False)
        st.bar_chart(prog_df.set_index("Mavzu"), height=280)

        st.divider()
        st.markdown("#### 📋 Mavzu bo'yicha batafsil")
        for topic in all_topics:
            score = prog.get(topic, 0)
            total_q = len([q for q in QUIZ_BANK if q["topic"]==topic])
            pct_t   = min(100, int(score/total_q*100)) if total_q else 0
            level   = "🥇 Expert" if pct_t>=80 else "🥈 O'rta" if pct_t>=40 else "🥉 Boshlang'ich"
            st.markdown(
                f'<div style="background:{T["bg_s"]};border:1px solid {T["bdr"]};'
                f'border-radius:8px;padding:12px 16px;margin-bottom:8px">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:6px">'
                f'<span style="color:{T["txt_p"]};font-weight:500">{topic}</span>'
                f'<span style="color:{T["txt_s"]};font-size:12px">{level} | {score}/{total_q} to\'g\'ri</span>'
                f'</div>'
                f'<div class="prog-bar"><div class="prog-fill" style="width:{pct_t}%"></div></div>'
                f'</div>', unsafe_allow_html=True)

        # Darajalar
        st.divider()
        total_score = sum(prog.values())
        overall_pct = int(total_score / len(QUIZ_BANK) * 100) if QUIZ_BANK else 0
        badge_level = ("🏆 Python Expert" if overall_pct>=80 else
                       "🥈 Intermediate"   if overall_pct>=50 else
                       "🥉 Beginner")
        st.markdown(f'<div class="card-green" style="text-align:center">'
                    f'<div style="font-size:32px">{badge_level.split()[0]}</div>'
                    f'<h3 style="color:{T["txt_p"]}">{badge_level}</h3>'
                    f'<p style="color:{T["txt_s"]}">Umumiy daraja: {overall_pct}% | '
                    f'{total_score} to\'g\'ri javob</p>'
                    f'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 8 — MULTI-MODEL
# ══════════════════════════════════════════════
with tab_multi:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">⚖️</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Multi-Model Solishtirish</span>'
                f'<span class="badge b-orange">Beta</span></div>', unsafe_allow_html=True)

    st.caption("Bir xil savolga bir necha model javob beradi — yonma-yon ko'rasiz.")

    mm_models = st.multiselect("🤖 Modellarni tanlang (2-4):", MODELS,
                                default=MODELS[:2], max_selections=4)
    mm_prompt = st.text_area("📝 Savol yoki kod:", height=140,
                              placeholder="Fibonacci funksiyasini yozing...")
    mm_sys    = st.selectbox("🎯 Tizim prompt:", list(MENTOR_PROMPTS.keys()))

    if st.button("🚀 Barcha modellarda ishlatish", use_container_width=False):
        if not mm_prompt.strip():
            st.warning("⚠️ Savol kiriting!")
        elif len(mm_models) < 2:
            st.warning("⚠️ Kamida 2 ta model tanlang!")
        else:
            results = {}
            prog_ph = st.progress(0)
            for idx, mdl in enumerate(mm_models):
                with st.spinner(f"🤖 {mdl} javob bermoqda..."):
                    try:
                        resp = simple_ai(mm_prompt, MENTOR_PROMPTS[mm_sys], mdl, temperature)
                        results[mdl] = resp
                        log_api(count_tokens(mm_prompt+resp))
                    except Exception as e:
                        results[mdl] = f"❌ Xatolik: {e}"
                prog_ph.progress((idx+1)/len(mm_models))
            st.session_state.multi_results = results
            prog_ph.empty()

    if st.session_state.multi_results:
        st.divider()
        st.markdown("**📊 Natijalar:**")
        cols = st.columns(len(st.session_state.multi_results))
        for col, (mdl, resp) in zip(cols, st.session_state.multi_results.items()):
            with col:
                short = mdl.split("-")[1] if "-" in mdl else mdl[:10]
                st.markdown(f"**🤖 {short}**")
                st.markdown(f'<div class="card-blue" style="font-size:13px;max-height:400px;overflow-y:auto">{resp}</div>',
                            unsafe_allow_html=True)

        # Eng yaxshisini tanlash
        st.divider()
        best = st.radio("🏆 Qaysi javob yaxshiroq?",
                        list(st.session_state.multi_results.keys()), horizontal=True)
        if st.button("💬 Chat ga yuborish"):
            st.session_state.messages.append({
                "role":"assistant",
                "content":f"**{best} javobi:**\n{st.session_state.multi_results[best]}",
                "time":fmt_time()})
            st.success("✅ Chat ga yuborildi!")

# ══════════════════════════════════════════════
# TAB 9 — SHARE
# ══════════════════════════════════════════════
with tab_share:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🔗</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Kod Ulashish</span>'
                f'</div>', unsafe_allow_html=True)

    share_code = st.text_area("📝 Ulashmoqchi bo'lgan kodingiz:", height=200,
                               placeholder="# Ulashmoqchi bo'lgan kodingiz...")
    share_desc = st.text_input("📄 Tavsif (ixtiyoriy):", placeholder="Fibonacci recursive...")

    if st.button("🔗 Ulashish uchun ID yaratish", use_container_width=False):
        if share_code.strip():
            sid   = make_short_id(share_code + fmt_time())
            entry = {"code": share_code, "desc": share_desc or "No description",
                     "author": st.session_state.username, "time": fmt_time(),
                     "date": date.today().isoformat()}
            st.session_state.shared_codes[sid] = entry

            st.success(f"✅ ID yaratildi: `{sid}`")
            st.markdown(f'<div class="card-green">'
                        f'<strong>📋 Share ID:</strong> <code>{sid}</code><br>'
                        f'<strong>👤 Muallif:</strong> {st.session_state.username}<br>'
                        f'<strong>🕐 Vaqt:</strong> {fmt_time()}<br>'
                        f'<small style="color:{T["txt_s"]}">Bu ID ni do\'stingizga yuboring!</small>'
                        f'</div>', unsafe_allow_html=True)
            st.code(share_code, language="python")
        else:
            st.warning("⚠️ Kod kiriting!")

    st.divider()
    st.markdown("#### 📂 ID bo'yicha kod ochish")
    lookup_id = st.text_input("🔍 Share ID kiriting:", placeholder="a1b2c3d4",
                               max_chars=8)
    if st.button("🔍 Izlash"):
        if lookup_id in st.session_state.shared_codes:
            found = st.session_state.shared_codes[lookup_id]
            st.markdown(f'<div class="card-blue">'
                        f'<strong>👤 Muallif:</strong> {found["author"]}<br>'
                        f'<strong>📄 Tavsif:</strong> {found["desc"]}<br>'
                        f'<strong>🕐 Vaqt:</strong> {found["time"]}'
                        f'</div>', unsafe_allow_html=True)
            st.code(found["code"], language="python")
            sc1,sc2 = st.columns(2)
            with sc1:
                if st.button("▶️ Runner ga yuborish", key="share_run"):
                    st.session_state["runner_prefill"] = found["code"]
                    st.success("✅ Runner tabiga o'ting!")
            with sc2:
                if st.button("🤖 Copilot ga yuborish", key="share_cop"):
                    st.session_state["copilot_prefill"] = found["code"]
                    st.success("✅ Copilot tabiga o'ting!")
        elif lookup_id:
            st.error(f"❌ ID `{lookup_id}` topilmadi.")

    if st.session_state.shared_codes:
        st.divider()
        st.markdown(f"#### 📋 Saqlangan kodlar ({len(st.session_state.shared_codes)} ta)")
        for sid, entry in list(st.session_state.shared_codes.items()):
            with st.expander(f"🔗 `{sid}` — {entry['desc'][:40]} | {entry['author']}"):
                st.code(entry["code"], language="python")
                if st.button("🗑️ O'chirish", key=f"share_del_{sid}"):
                    del st.session_state.shared_codes[sid]
                    st.rerun()

# ══════════════════════════════════════════════
# TAB 10 — GITHUB
# ══════════════════════════════════════════════
with tab_github:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🐙</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">GitHub Fayl Tahlili</span>'
                f'</div>', unsafe_allow_html=True)

    st.caption("GitHub fayl URL ni tashlang — AI avtomatik o'qib tahlil qiladi.")

    gh_url = st.text_input("🔗 GitHub URL:",
                            placeholder="https://github.com/user/repo/blob/main/script.py")

    gh_action = st.radio("🎯 Amal:", [
        "📊 Umumiy tahlil", "🐛 Xatolar topish",
        "🔐 Xavfsizlik skaner", "📈 Complexity tahlil",
        "📖 Tushuntirish", "🔄 Refactoring tavsiyasi"
    ], horizontal=True)

    if st.button("🐙 GitHub dan yuklash va tahlil", use_container_width=False):
        if not gh_url.strip():
            st.warning("⚠️ GitHub URL kiriting!")
        elif "github.com" not in gh_url:
            st.error("❌ GitHub URL bo'lishi kerak!")
        else:
            with st.spinner("🐙 GitHub dan yuklanmoqda..."):
                code_text = fetch_github(gh_url)

            if code_text.startswith("❌"):
                st.error(code_text)
            else:
                st.success(f"✅ {len(code_text)} belgi yuklandi!")
                with st.expander("👁️ Fayl tarkibi"):
                    st.code(code_text[:3000] + ("..." if len(code_text)>3000 else ""),
                            language="python")

                action_sys = {
                    "📊 Umumiy tahlil":   MENTOR_PROMPTS["Code Reviewer 🔍"],
                    "🐛 Xatolar topish":  MENTOR_PROMPTS["Debug Ustasi 🐛"],
                    "🔐 Xavfsizlik skaner": COPILOT_PROMPTS["🔐 Xavfsizlik"],
                    "📈 Complexity tahlil":"O'zbek tilida har funksiya uchun Time/Space complexity tahlil qil.",
                    "📖 Tushuntirish":     COPILOT_PROMPTS["📖 Tushuntirish"],
                    "🔄 Refactoring tavsiyasi": COPILOT_PROMPTS["🔄 Refactoring"],
                }
                with st.spinner(f"🤖 {gh_action} bajarilmoqda..."):
                    try:
                        prompt_gh = f"Fayl: {gh_url}\n\nKod ({len(code_text)} belgi):\n```python\n{code_text[:5000]}\n```"
                        result    = simple_ai(prompt_gh, action_sys[gh_action], model_choice)
                        st.markdown(f"**{gh_action} natijasi:**")
                        cls = {"📊":"card-blue","🐛":"card-orange","🔐":"card-orange",
                               "📈":"card-green","📖":"card-green","🔄":"card-purple"}
                        card_cls = next((v for k,v in cls.items() if gh_action.startswith(k)), "card-blue")
                        st.markdown(f'<div class="{card_cls}">{result}</div>',
                                    unsafe_allow_html=True)
                        log_api(count_tokens(prompt_gh+result))
                    except Exception as e:
                        st.error(f"❌ {e}")

    with st.expander("💡 Misol GitHub URL lar"):
        st.markdown("""
```
https://github.com/python/cpython/blob/main/Lib/collections/__init__.py
https://github.com/pallets/flask/blob/main/src/flask/app.py
https://github.com/django/django/blob/main/django/db/models/base.py
```
⚠️ Faqat public repolar ishlaydi. Max ~5000 belgi tahlil qilinadi.
        """)

# ══════════════════════════════════════════════
# TAB 11 — DAILY CHALLENGE
# ══════════════════════════════════════════════
with tab_challenge:
    import random as _rnd2
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span style="font-size:26px">🗓️</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Kunlik Muammo</span>'
                f'<span class="badge b-orange">Daily Challenge</span></div>', unsafe_allow_html=True)

    # Kunlik muammoni tanlash (kun asosida seed)
    today_seed = int(date.today().strftime("%Y%m%d"))
    _rnd2.seed(today_seed)
    today_challenge = DAILY_CHALLENGES[_rnd2.randint(0, len(DAILY_CHALLENGES)-1)]
    _rnd2.seed()  # seedni tiklash

    if st.session_state.daily_challenge is None:
        st.session_state.daily_challenge = today_challenge

    ch = st.session_state.daily_challenge

    # Challenge karta
    diff_colors = {"🟢 Oson":"b-green","🟡 O'rta":"b-orange","🔴 Qiyin":"b-purple"}
    diff_cls    = diff_colors.get(ch["difficulty"], "b-blue")

    st.markdown(f"""
    <div style="background:{T['bg_s']};border:1px solid {T['bdr']};border-radius:16px;padding:24px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <span class="badge {diff_cls}">{ch['difficulty']}</span>
        <span style="color:{T['txt_s']};font-size:12px">📅 {date.today().strftime('%d.%m.%Y')}</span>
      </div>
      <h3 style="color:{T['txt_p']};margin:0 0 12px">🎯 {ch['title']}</h3>
      <p style="color:{T['txt_s']};font-size:14px;line-height:1.7">{ch['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    show_hint = st.checkbox("💡 Maslahat ko'rsatish")
    if show_hint:
        st.markdown(f'<div class="card-blue">💡 <strong>Maslahat:</strong> <code>{ch["hint"]}</code></div>',
                    unsafe_allow_html=True)

    st.markdown("**📝 Yechimingizni yozing:**")
    challenge_code = st.text_area("", height=220,
                                   placeholder=f"# {ch['title']} yechimi\ndef solution():\n    pass",
                                   key="challenge_code", label_visibility="collapsed")

    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        if st.button("▶️ Bajarish", use_container_width=True, key="ch_run"):
            if challenge_code.strip():
                with st.spinner("⚙️ Bajarilmoqda..."):
                    out, err = run_piston(challenge_code)
                if out:
                    st.markdown(f'<div class="run-out">{out}</div>', unsafe_allow_html=True)
                if err:
                    st.markdown(f'<div class="run-out run-err">{err}</div>', unsafe_allow_html=True)
    with cc2:
        if st.button("🤖 AI tekshirsin", use_container_width=True, key="ch_check"):
            if challenge_code.strip():
                with st.spinner("🤖 Tekshirilmoqda..."):
                    try:
                        check_sys = f"""Sen Python muammo tekshiruvchisisan.
Muammo: {ch['desc']}
Foydalanuvchi yechimini tekshir:
1. Muammo to'g'ri hal qilinganmi? (Ha/Yo'q)
2. Edge caseslar ko'rib chiqilganmi?
3. Complexity qanday?
4. Yaxshilash tavsiyalari
O'zbek tilida javob ber."""
                        feedback = simple_ai(challenge_code, check_sys, model_choice)
                        st.markdown(f'<div class="card-green">{feedback}</div>',
                                    unsafe_allow_html=True)
                        if not st.session_state.daily_done:
                            st.session_state.daily_done = True
                            db_save_progress(st.session_state.username, "Challenge", 2)
                            st.session_state.progress_topics = db_load_progress(st.session_state.username)
                            st.balloons()
                            st.success("🎉 Challenge bajarildi! +2 ball qo'shildi!")
                    except Exception as e:
                        st.error(f"❌ {e}")
    with cc3:
        if st.button("💡 AI yechimi", use_container_width=True, key="ch_sol"):
            with st.spinner("💡 Yechim tayyorlanmoqda..."):
                try:
                    sol_sys = f"Quyidagi Python muammosini optimal yechimini ko'rsat: {ch['desc']}\nType hints, docstring va complexity izoh bilan. O'zbek tilida izoh."
                    solution = simple_ai(ch["desc"], sol_sys, model_choice)
                    st.code(solution, language="python")
                except Exception as e:
                    st.error(f"❌ {e}")

    st.divider()
    st.markdown("#### 🗓️ Boshqa challengelar")
    for i, c2 in enumerate(DAILY_CHALLENGES):
        if c2["title"] != ch["title"]:
            if st.button(f"{c2['difficulty']} {c2['title']}", key=f"ch_{i}"):
                st.session_state.daily_challenge = c2
                st.session_state.daily_done = False
                st.rerun()

# ══════════════════════════════════════════════
# TAB 12 — DASHBOARD
# ══════════════════════════════════════════════
with tab_dash:
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">'
                f'<span style="font-size:26px">📊</span>'
                f'<span style="color:{T["txt_p"]};font-size:18px;font-weight:700">Dashboard</span>'
                f'<span class="badge b-green">Live</span></div>', unsafe_allow_html=True)

    # Metrikalar
    dm = st.columns(6)
    dm[0].metric("💬 Xabar",    len(st.session_state.messages))
    dm[1].metric("🔄 Suhbat",   st.session_state.conversation_count)
    dm[2].metric("🪙 Token",    f"~{st.session_state.total_tokens:,}")
    dm[3].metric("🏆 Quiz",     f"{quiz_pct}%")
    dm[4].metric("✂️ Snippet",  len(st.session_state.snippets))
    dm[5].metric("🔗 Shared",   len(st.session_state.shared_codes))
    st.divider()

    dl, dr = st.columns(2)
    with dl:
        st.markdown("#### 📈 Token sarfi")
        calls = st.session_state.dashboard_api_calls
        if calls:
            df = pd.DataFrame(calls)
            df.index = range(1, len(df)+1)
            st.bar_chart(df["tokens"], height=200)
            st.caption(f"Jami {len(calls)} chaqiruv | ~{df['tokens'].sum():,} token")
        else:
            st.info("Hali API chaqiruvlar yo'q.")

    with dr:
        st.markdown("#### 🗂️ Suhbat tarkibi")
        if st.session_state.messages:
            u = sum(1 for m in st.session_state.messages if m["role"]=="user")
            a = sum(1 for m in st.session_state.messages if m["role"]=="assistant")
            st.bar_chart(pd.DataFrame({"Soni":{"👤 Foydalanuvchi":u,"🐍 AI":a}}), height=200)
        else:
            st.info("Hali suhbat yo'q.")

    st.divider()

    dl2, dr2 = st.columns(2)
    with dl2:
        st.markdown("#### 🏆 Quiz natijalari (mavzu)")
        if st.session_state.progress_topics:
            prog_df = pd.DataFrame([
                {"Mavzu": t, "Ball": v}
                for t, v in st.session_state.progress_topics.items()
            ]).sort_values("Ball", ascending=False)
            st.bar_chart(prog_df.set_index("Mavzu"), height=200)
        else:
            st.info("Quiz hali boshlanmagan.")

    with dr2:
        st.markdown("#### 🥇 Daraja")
        total_s = sum(st.session_state.progress_topics.values()) if st.session_state.progress_topics else 0
        overall = int(total_s / len(QUIZ_BANK) * 100) if QUIZ_BANK else 0
        badge = ("🏆 Python Expert" if overall>=80 else
                 "🥈 Intermediate"   if overall>=50 else "🥉 Beginner")
        st.markdown(f'<div class="card-green" style="text-align:center;padding:30px">'
                    f'<div style="font-size:40px">{badge.split()[0]}</div>'
                    f'<h3 style="color:{T["txt_p"]};margin:8px 0">{badge}</h3>'
                    f'<p style="color:{T["txt_s"]}">{overall}% | {total_s} ball</p>'
                    f'</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 💾 Saqlangan sessiyalar")
    if st.session_state.saved_sessions:
        for i, sess in enumerate(st.session_state.saved_sessions):
            with st.expander(f"📁 {sess['name']} — {sess['date']} ({sess['count']} xabar)"):
                for m in sess["messages"][:2]:
                    icon = "👤" if m["role"]=="user" else "🐍"
                    st.markdown(f"**{icon}:** {m['content'][:100]}...")
                sc1,sc2 = st.columns(2)
                with sc1:
                    if st.button("📂 Yuklash", key=f"dash_load_{i}"):
                        st.session_state.messages = sess["messages"].copy()
                        st.success("✅ Yuklandi!"); st.rerun()
                with sc2:
                    if st.button("🗑️ O'chirish", key=f"dash_del_{i}"):
                        st.session_state.saved_sessions.pop(i)
                        db_set(st.session_state.username,
                               {**db_get(st.session_state.username),
                                "sessions": st.session_state.saved_sessions})
                        st.rerun()
    else:
        st.info("💾 Sidebar dagi 'Saqlash' tugmasidan sessiyalarni saqlang.")

    st.divider()
    st.markdown(f'<p style="color:{T["txt_s"]};font-size:11px;text-align:center">'
                f'🐍 AI Python Mentor PRO v5.0 | Muallif: {st.session_state.username}<br>'
                f'Powered by Groq API + Piston API | Magistr/Researcher</p>',
                unsafe_allow_html=True)
