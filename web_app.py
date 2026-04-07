import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        # API ni sozlash
        genai.configure(api_key=api_key_input)
        
        # MUHIM: API versiyasini majburan 'v1' ga o'tkazamiz
        # Bu 404 xatosini yo'qotishning eng samarali yo'li
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            # Versiya xatosini chetlab o'tish:
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300)
            if st.button("Tahlil qilish 🔍"):
                if not kod.strip():
                    st.warning("Iltimos, avval kod yozing!")
                else:
                    xato_matni = "Xato yo'q"
                    try:
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    with st.spinner('AI bilan bog\'lanmoqda...'):
                        try:
                            # Sokratik javob so'rash
                            prompt = f"Talaba kodi: {kod}\nXato: {xato_matni}\nO'zbek tilida Sokratik savol ber."
                            
                            # API versiyasini v1 qilib ko'rsatamiz
                            response = model.generate_content(
                                prompt,
                                request_options=RequestOptions(api_version='v1')
                            )
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI model bilan bog'lanishda muammo: {ai_err}")
                            st.info("Maslahat: Google AI Studio'da API kalit yonidagi 'Enable API' tugmasi bosilganini tekshiring.")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ API Key kiriting!")
