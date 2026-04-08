"""
AI Python Mentor - Professional Streamlit Application
Muallif: Jaloliddin | Magistr/Researcher
Versiya: 2.0.0 (Mukammal)
"""

import streamlit as st
from groq import Groq
import time
import json
from datetime import datetime
import re

# ============================================================
# 1. SAHIFA SOZLAMALARI
# ============================================================
st.set_page_config(
    page_title="AI Python Mentor",
    layout="wide",
    page_icon="🐍",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": None,
        "About": "AI Python Mentor v2.0 | Jaloliddin tomonidan yaratilgan"
    }
)

# ============================================================
# 2. MAXFIY KALIT VA CLIENT SOZLASH
# ============================================================
def get_groq_client():
    """Groq clientini xavfsiz yaratish."""
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        return None, None
    try:
        client = Groq(api_key=api_key)
        return client, api_key
    except Exception as e:
        st.error(f"Client yaratishda xatolik: {e}")
        return None, None

client, api_key = get_groq_client()

# ============================================================
# 3. PROFESSIONAL CSS DIZAYN
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* Asosiy rang paleti */
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #1c2128;
    --accent-green: #00d4aa;
    --accent-blue: #4f9cf9;
    --accent-purple: #bc8cff;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --border-color: #30363d;
    --success: #3fb950;
    --warning: #d29922;
    --error: #f85149;
}

/* Umumiy fon */
.stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'Inter', sans-serif;
}

/* Sarlavha */
h1 {
    background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* Chat xabar konteynerlar */
.stChatMessage {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 8px !important;
}

/* Foydalanuvchi xabari */
[data-testid="stChatMessageContent"] {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
}

/* Chat input */
.stChatInputContainer {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

.stChatInputContainer textarea {
    color: var(--text-primary) !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* Metrik kartalar */
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
    padding: 8px 16px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0, 212, 170, 0.3) !important;
}

/* Kod bloklari */
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

/* Select box */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

/* Slider */
.stSlider > div > div > div {
    background: var(--accent-green) !important;
}

/* Info/Warning/Error boxlar */
.stAlert {
    border-radius: 8px !important;
    border: none !important;
}

/* Divider */
hr {
    border-color: var(--border-color) !important;
    margin: 16px 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: var(--bg-primary);
}
::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid rgba(63, 185, 80, 0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: #3fb950;
    font-weight: 500;
}

.status-dot {
    width: 6px;
    height: 6px;
    background: #3fb950;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. SESSION STATE ISHGA TUSHIRISH
# ============================================================
def init_session_state():
    """Barcha session state o'zgaruvchilarini boshlash."""
    defaults = {
        "messages": [],
        "total_tokens_used": 0,
        "session_start": datetime.now().strftime("%H:%M"),
        "conversation_count": 0,
        "last_model": "llama-3.3-70b-versatile",
        "error_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================
# 5. SYSTEM PROMPT (KUCHLI VA ANIQ)
# ============================================================
SYSTEM_PROMPTS = {
    "Python Mentor 🐍": """Sen magistr darajasidagi tajribali Python arxitektisan va mentorsan.

ASOSIY VAZIFALAR:
1. Kod tahlili: Time/Space complexity (Big-O notatsiya), PEP8, SOLID prinsiplari
2. Xavfsizlik: SQL injection, XSS, input validation zaifliklarini topish
3. Optimizatsiya: Memory leak, bottleneck, anti-pattern larni aniqlash
4. Best practices: Design pattern tavsiyalari, clean code printsiplari
5. Debug yordam: Error xabarlarini tushuntirish va yechim taklif qilish

JAVOB FORMATI:
- Har doim O'zbek tilida javob ber
- Kod namunalar bilan izohlash
- Muammoni → Yechimni → Natijani ko'rsatish
- Murakkab mavzularni oddiy til bilan tushuntirish

CHEKLOVLAR:
- Faqat Python va dasturlash haqida gapirish
- Hech qachon noto'g'ri ma'lumot bermaslik
- Noaniq bo'lsa, aniqlashtirish so'rash""",

    "Code Reviewer 🔍": """Sen yuqori malakali Code Review mutaxassisisan.

Har bir kod uchun quyidagi format bilan javob ber:

## 📊 Umumiy Baho: X/10

## ✅ Yaxshi tomonlar:
- [ro'yxat]

## ⚠️ Kamchiliklar:
- [ro'yxat]

## 🔧 Tavsiya etilgan yaxshilangan kod:
```python
# yaxshilangan kod
```

## 📈 Complexity tahlili:
- Time: O(?)
- Space: O(?)

Faqat O'zbek tilida yozish.""",

    "Debug Ustasi 🐛": """Sen Python debug va xato tuzatish ekspertisan.

Har bir xato uchun:
1. 🔍 Xato sababi (aniq va tushunarli)
2. 📍 Qayerda yuz berdi (fayl/qator)
3. 🔧 Bosqichma-bosqich yechim
4. 💡 Kelajakda oldini olish usullari
5. ✅ Tuzatilgan kod

Faqat O'zbek tilida yozish.""",

    "Algoritm Muallimi 📚": """Sen Data Structures va Algorithms bo'yicha professor darajasidagi o'qituvchisan.

Mavzuni tushuntirishda:
1. Nazariya (oddiy til bilan)
2. Vizual tushuntirish (ASCII art bilan)
3. Python implementatsiya
4. Complexity tahlili
5. Real hayot misollari
6. Mashq savollari

Faqat O'zbek tilida yozish."""
}

# ============================================================
# 6. YORDAMCHI FUNKSIYALAR
# ============================================================
def count_tokens_estimate(text: str) -> int:
    """Taxminiy token soni hisoblash (1 token ≈ 4 belgi)."""
    return len(text) // 4

def contains_code(text: str) -> bool:
    """Matnda kod borligini tekshirish."""
    return "```" in text or "def " in text or "import " in text or "class " in text

def format_message_time() -> str:
    """Hozirgi vaqtni formatlash."""
    return datetime.now().strftime("%H:%M")

def export_chat_history() -> str:
    """Chat tarixini JSON formatda eksport qilish."""
    export_data = {
        "export_time": datetime.now().isoformat(),
        "session_start": st.session_state.session_start,
        "total_messages": len(st.session_state.messages),
        "messages": st.session_state.messages
    }
    return json.dumps(export_data, ensure_ascii=False, indent=2)

def get_ai_response(
    client: Groq,
    messages: list,
    system_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    use_streaming: bool
):
    """AI dan javob olish (streaming yoki normal).
    
    MUHIM: Groq API faqat 'role' va 'content' maydonlarini qabul qiladi.
    'time', 'model' kabi qo'shimcha maydonlarni filterlash kerak.
    """
    # Faqat API uchun kerakli maydonlarni olish
    clean_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages
    ]
    
    messages_for_api = [
        {"role": "system", "content": system_prompt}
    ] + clean_messages

    completion = client.chat.completions.create(
        model=model,
        messages=messages_for_api,
        stream=use_streaming,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
    )
    return completion

# ============================================================
# 7. SARLAVHA
# ============================================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title("🐍 AI Python Mentor")
    st.caption("Magistratura darajasidagi intellektual dasturlash yordamchisi")
with col_status:
    if api_key:
        st.markdown(
            '<div class="status-badge"><span class="status-dot"></span> Online</div>',
            unsafe_allow_html=True
        )
    else:
        st.error("⚠️ Offline")

st.divider()

# ============================================================
# 8. SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Sozlamalar")

    # Mentor rejimi
    mentor_mode = st.selectbox(
        "🎯 Mentor rejimi",
        options=list(SYSTEM_PROMPTS.keys()),
        help="Har bir rejim turli javob formati beradi"
    )

    st.divider()

    # Model tanlash
    model_choice = st.selectbox(
        "🤖 AI Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        help="Katta modellar = aniqroq, lekin sekinroq"
    )

    # Parametrlar
    temperature = st.slider(
        "🌡️ Ijodkorlik darajasi",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Past = aniq/texnik | Yuqori = ijodiy/keng"
    )

    max_tokens = st.select_slider(
        "📏 Maksimal javob uzunligi",
        options=[512, 1024, 2048, 4096, 8192],
        value=2048,
        help="Uzun kodlar uchun 4096+ tanlang"
    )

    max_history = st.slider(
        "💬 Tariх uzunligi (xabarlar)",
        min_value=2,
        max_value=30,
        value=10,
        step=2,
        help="Ko'p = ko'proq kontekst, lekin ko'proq token"
    )

    use_streaming = st.toggle(
        "⚡ Streaming (real-vaqt javob)",
        value=True,
        help="Yoqilsa javob harfma-harf chiqadi"
    )

    st.divider()

    # Statistika
    st.markdown("### 📊 Sessiya statistikasi")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Xabarlar", len(st.session_state.messages))
    with col2:
        st.metric("🔄 Suhbatlar", st.session_state.conversation_count)

    st.metric(
        "🪙 Taxminiy tokenlar",
        f"~{st.session_state.total_tokens_used:,}"
    )
    st.metric("⏰ Sessiya boshlandi", st.session_state.session_start)

    st.divider()

    # Amallar
    st.markdown("### 🛠️ Amallar")

    if st.button("🗑️ Suhbatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens_used = 0
        st.session_state.conversation_count = 0
        st.success("✅ Tozalandi!")
        time.sleep(0.5)
        st.rerun()

    # Export tugmasi
    if st.session_state.messages:
        export_data = export_chat_history()
        st.download_button(
            label="📥 Tarixni saqlash (JSON)",
            data=export_data,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.divider()

    # Tezkor savollar
    st.markdown("### 💡 Tezkor savollar")
    quick_questions = [
        "Python list vs tuple farqi?",
        "GIL nima va u nima uchun kerak?",
        "Decorator qanday ishlaydi?",
        "async/await tushuntir",
        "@staticmethod vs @classmethod",
    ]
    for q in quick_questions:
        if st.button(q, use_container_width=True, key=f"quick_{q}"):
            st.session_state["quick_prompt"] = q
            st.rerun()

    st.divider()
    st.markdown(
        '<p style="color: #8b949e; font-size: 11px; text-align: center;">'
        '🐍 AI Python Mentor v2.0<br>Muallif: Jaloliddin<br>Magistr/Researcher</p>',
        unsafe_allow_html=True
    )

# ============================================================
# 9. ASOSIY CHAT INTERFEYSI
# ============================================================
if not api_key:
    st.warning("⚠️ **Sozlash kerak:** Streamlit Secrets bo'limiga `GROQ_API_KEY` qo'shing.")
    st.code("""
# .streamlit/secrets.toml faylida:
GROQ_API_KEY = "gsk_your_key_here"
    """, language="toml")
    st.info("🔑 Groq API kalitini https://console.groq.com dan oling (bepul!)")
    st.stop()

# Bo'sh suhbat uchun xush kelibsiz xabari
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; color: #8b949e;">
        <h2 style="color: #e6edf3; font-size: 24px;">Salom! Men sizning AI Python Mentoringizman 👋</h2>
        <p style="font-size: 15px; max-width: 600px; margin: 0 auto;">
            Python haqida istalgan savol bering, kodingizni tahlil qildiring yoki 
            algoritmlar haqida bilib oling. Chap paneldagi tezkor savollardan ham foydalanishingiz mumkin.
        </p>
        <br>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 20px;">
            <span style="background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 8px 16px; font-size: 13px;">🔍 Kod tahlili</span>
            <span style="background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 8px 16px; font-size: 13px;">🐛 Debug yordam</span>
            <span style="background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 8px 16px; font-size: 13px;">📚 Algoritm ta'lim</span>
            <span style="background: #1c2128; border: 1px solid #30363d; border-radius: 8px; padding: 8px 16px; font-size: 13px;">⚡ Optimizatsiya</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Avvalgi xabarlarni ko'rsatish
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🐍"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        # Vaqt ko'rsatish
        if "time" in message:
            st.caption(f"🕐 {message['time']}")

# ============================================================
# 10. CHAT INPUT VA AI JAVOB
# ============================================================

# Tezkor savol yoki oddiy input
prompt = None

if "quick_prompt" in st.session_state and st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

user_input = st.chat_input(
    "Python bo'yicha savol bering, kodingizni tashlang yoki xato xabarini yuboring...",
    key="main_chat_input"
)

if user_input:
    prompt = user_input

# Promptni qayta ishlash
if prompt:
    msg_time = format_message_time()

    # Foydalanuvchi xabarini saqlash
    user_message = {
        "role": "user",
        "content": prompt,
        "time": msg_time
    }
    st.session_state.messages.append(user_message)

    # Tokenlarni hisoblash
    st.session_state.total_tokens_used += count_tokens_estimate(prompt)

    # Foydalanuvchi xabarini ko'rsatish
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.caption(f"🕐 {msg_time}")

    # AI javobini generatsiya qilish
    with st.chat_message("assistant", avatar="🐍"):
        message_placeholder = st.empty()
        full_response = ""
        response_time = format_message_time()

        try:
            # Tariхni cheklash
            recent_messages = st.session_state.messages[-max_history:]

            # Kod aniqlanganida maxsus signal
            if contains_code(prompt):
                message_placeholder.markdown("*🔍 Kodingiz tahlil qilinmoqda...*")

            # AI dan javob olish
            completion = get_ai_response(
                client=client,
                messages=recent_messages,
                system_prompt=SYSTEM_PROMPTS[mentor_mode],
                model=model_choice,
                temperature=temperature,
                max_tokens=max_tokens,
                use_streaming=use_streaming
            )

            if use_streaming:
                # Streaming rejimi
                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta.content:
                        delta = chunk.choices[0].delta.content
                        full_response += delta
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            else:
                # Normal rejim
                with st.spinner("🤔 Javob tayyorlanmoqda..."):
                    full_response = completion.choices[0].message.content
                message_placeholder.markdown(full_response)

            # Vaqtni ko'rsatish
            st.caption(f"🕐 {response_time} | 🤖 {model_choice}")

            # AI javobini tarixga saqlash
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "time": response_time,
                "model": model_choice
            })

            # Statistikani yangilash
            st.session_state.total_tokens_used += count_tokens_estimate(full_response)
            st.session_state.conversation_count += 1
            st.session_state.last_model = model_choice
            st.session_state.error_count = 0  # Muvaffaqiyatli - xato sonini tiklash

        except Exception as e:
            error_msg = str(e)
            st.session_state.error_count += 1

            # Xatoni aniq tushuntirish
            if "rate_limit" in error_msg.lower():
                st.error("⏱️ **Rate limit:** So'rovlar juda tez yuborildi. 30 soniya kuting.")
            elif "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                st.error("🔑 **API kalit xatosi:** GROQ_API_KEY noto'g'ri. Tekshiring.")
            elif "model_not_found" in error_msg.lower():
                st.error(f"🤖 **Model topilmadi:** `{model_choice}` mavjud emas.")
            elif "context_length" in error_msg.lower():
                st.error("📏 **Kontekst limitdan oshdi:** Suhbatni tozalang yoki tariх uzunligini kamaytiring.")
            else:
                st.error(f"❌ **Xatolik yuz berdi:** {error_msg}")
                st.info("💡 Muammo davom etsa: 1) API kalitni tekshiring 2) Modelni o'zgartiring 3) Suhbatni tozalang")

            # Ko'p xato bo'lsa ogohlantirish
            if st.session_state.error_count >= 3:
                st.warning("⚠️ Bir necha marta xato yuz berdi. API kalitingizni va tarmoq ulanishingizni tekshiring.")
