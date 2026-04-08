import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide", page_icon="🎓")

# Streamlit Secrets'dan kalitni tekshiramiz
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = None

st.title("🎓 Intellektual Python Repetitori")
st.markdown("---")

# 2. Yon panel
with st.sidebar:
    st.header("⚙️ Ma'lumot")
    st.write("Bu bot sizga Python dasturlash tilini o'rganishda yordam beradi.")
    st.write("Dasturchi: **Mushtariy**")
    st.markdown("---")
    if api_key:
        st.success("✅ Tizim tayyor (API ulandi)")
    else:
        st.error("❌ API kalit topilmadi! Streamlit Secrets'ni sozlang.")

# 3. Asosiy mantiq
if api_key:
    try:
        client = Groq(api_key=api_key)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Kod yozish maydoni")
            kod = st.text_area("Python kodingizni shu yerga yozing:", height=350, placeholder="Masalan: print('Salom')")
            tugma = st.button("Tahlil qilish 🔍", use_container_width=True)

        if tugma:
            if not kod.strip():
                st.warning("Iltimos, avval kod yozing!")
            else:
                # Koddagi xatolikni tekshirish
                xato_info = "Kodda sintaktik xato yo'q."
                try:
                    exec(kod, {})
                except Exception as e:
                    xato_info = f"{type(e).__name__}: {str(e)}"
                
                with st.spinner("AI kodingizni o'rganmoqda..."):
                    try:
                        # Eng yangi model nomi
                        completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "Sen o'zbek tilida gapiradigan mohir Python o'qituvchisisan. Talabaga xatoni darrov aytma, savollar bilan yo'naltir."
                                },
                                {
                                    "role": "user", 
                                    "content": f"Kod: {kod}\nXato: {xato_info}"
                                }
                            ],
                            model="llama-3.3-70b-versatile",
                        )
                        with col2:
                            st.subheader("🤖 AI Repetitor maslahati:")
                            st.success(completion.choices[0].message.content)
                            
                    except Exception as ai_err:
                        st.error(f"AI bilan bog'lanishda xato: {ai_err}")

    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.info("Iltimos, avval Streamlit Cloud dashboard'da API kalitni sozlang.")

st.markdown("---")
st.caption("© 2026 Python AI Tutor | Mushtariy")
