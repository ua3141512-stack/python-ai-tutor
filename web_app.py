import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide", page_icon="🎓")

# Sahifa sarlavhasi
st.title("🎓 Intellektual Python Repetitori")
st.markdown("---")

# 2. Yon panel (Sidebar) sozlamalari
with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # API kalit kiritish joyi
    api_key_input = st.text_input("Groq API Keyni kiriting:", type="password").strip()
    
    st.write("---")
    st.info("""
    **Qanday ishlatiladi?**
    1. Groq API kalitingizni kiriting.
    2. Python kodingizni yozing.
    3. 'Tahlil qilish' tugmasini bosing.
    """)
    st.write("👨‍💻 Dasturchi: **Jaloliddin**")

# 3. Asosiy mantiq
if api_key_input:
    try:
        # Groq mijozini yaratish
        client = Groq(api_key=api_key_input)

        # Ekranni ikki ustunga bo'lamiz
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
                xato_matni = "Kodda sintaktik xato yo'q."
                try:
                    # Kodni vaqtincha tekshirib ko'ramiz
                    exec(kod, {})
                except Exception as e:
                    xato_matni = f"{type(e).__name__}: {str(e)}"
                
                # AI dan tahlil so'raymiz
                with st.spinner("AI kodingizni o'rganmoqda..."):
                    try:
                        # Modelga so'rov yuborish
                        completion = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "Sen o'zbek tilida gapiradigan mohir Python o'qituvchisisan. Talabaga xatoni darrov aytma, Sokratik usulda savollar berib uni o'ylashga majbur qil va yordam ber."
                                },
                                {
                                    "role": "user", 
                                    "content": f"Talaba kodi: {kod}\nXato haqida ma'lumot: {xato_matni}\nUnga o'zbek tilida yordam ber."
                                }
                            ],
                            model="llama3-8b-8192",
                        )
                        
                        with col2:
                            st.subheader("🤖 AI Repetitor maslahati:")
                            st.success(completion.choices[0].message.content)
                            
                    except Exception as ai_err:
                        st.error(f"AI bilan bog'lanishda xato: {ai_err}")

    except Exception as e:
        st.error(f"Tizim xatosi yuz berdi: {e}")
else:
    st.warning("⚠️ Davom etish uchun yon panelda Groq API Keyni kiriting!")

# Pastki qism
st.markdown("---")
st.caption("© 2026 Python AI Tutor - Barcha huquqlar himoyalangan.")
