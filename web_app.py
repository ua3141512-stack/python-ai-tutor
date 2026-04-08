import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Python Tutor", layout="wide", page_icon="🎓")

st.title("🎓 Intellektual Python Repetitori")
st.markdown("---")

with st.sidebar:
st.header("⚙️ Sozlamalar")
api_key_input = st.text_input("Groq API Keyni kiriting:", type="password").strip()
st.write("---")
st.info("Dasturchi: Jaloliddin")

if api_key_input:
try:
client = Groq(api_key=api_key_input)
col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Kod yozish maydoni")
        kod = st.text_area("Python kodingizni yozing:", height=350)
        tugma = st.button("Tahlil qilish 🔍", use_container_width=True)

    if tugma:
        if not kod.strip():
            st.warning("Iltimos, kod yozing!")
        else:
            xato_matni = "Kodda sintaktik xato yo'q."
            try:
                exec(kod, {})
            except Exception as e:
                xato_matni = f"{type(e).__name__}: {str(e)}"
            
            with st.spinner("AI o'rganmoqda..."):
                try:
                    completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "Sen o'zbek tilida gapiradigan mohir Python o'qituvchisisan. Sokratik usulda yordam ber."},
                            {"role": "user", "content": f"Kod: {kod}\nXato: {xato_matni}"}
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    with col2:
                        st.subheader("🤖 AI javobi:")
                        st.success(completion.choices[0].message.content)
                except Exception as ai_err:
                    st.error(f"AI xatosi: {ai_err}")
except Exception as e:
    st.error(f"Tizim xatosi: {e}")
else:
st.warning("⚠️ Groq API Keyni kiriting!")

st.markdown("---")
st.caption("© 2026 Python AI Tutor")
