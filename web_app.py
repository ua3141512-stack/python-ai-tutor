import streamlit as st
import google.generativeai as genai
from database_manager import DatabaseManager
import pandas as pd

# Sahifa dizayni
st.set_page_config(page_title="AI Python Tutor", layout="wide", initial_sidebar_state="expanded")

db = DatabaseManager()

# Sarlavha
st.title("🎓 Intellektual Python Repetitori")
st.info("Kodingizni tahlil qiling va sun'iy intellektdan metodik yordam oling.")

# Sidebar - Sozlamalar
with st.sidebar:
    st.header("⚙️ Sozlamalar")
    api_key = st.text_input("Gemini API Key:", type="password")
    st.markdown("---")
    if st.button("Bazani ko'rish"):
        st.session_state.show_db = True
    if st.button("Asosiy oyna"):
        st.session_state.show_db = False

# Asosiy mantiq
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if st.session_state.get('show_db', False):
        st.subheader("📊 Tahlillar tarixi (Ma'lumotlar bazasi)")
        # Bazadan ma'lumotlarni o'qish (database_manager'da select funksiyasi kerak bo'ladi)
        # Hozircha namunaviy jadval:
        st.warning("Bu bo'limda talabalar qilgan barcha xatolar statistikasi ko'rinadi.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300)
            if st.button("Tahlil qilish 🔍"):
                # Kodni tekshirish
                xato = "Xato yo'q"
                try:
                    exec(kod)
                except Exception as e:
                    xato = f"{type(e).__name__}: {str(e)}"
                
                # AI dan javob olish
                prompt = f"Talaba kodi: {kod}. Xato: {xato}. O'zbekcha Sokratik savol ber."
                response = model.generate_content(prompt)
                
                # Natijani chiqarish
                with col2:
                    st.subheader("🤖 AI Repetitor javobi:")
                    st.code(xato, language="python")
                    st.write(response.text)
                    db.saqlash(xato, kod)
else:
    st.warning("Iltimos, chap tomondagi menyuga API Key kiriting!")