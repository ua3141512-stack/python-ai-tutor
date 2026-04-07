import streamlit as st
import google.generativeai as genai

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # API keyni probellarsiz kiriting
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        # API ni eng sodda usulda sozlash
        genai.configure(api_key=api_key_input)
        
        # FAQAT model nomi, hech qanday qo'shimcha argumentlarsiz
        model = genai.GenerativeModel('gemini-1.5-flash')

        col1, col2 = st.columns([1, 1])
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300)
            if st.button("Tahlil qilish 🔍"):
                if not kod.strip():
                    st.warning("Iltimos, avval kod yozing!")
                else:
                    # 1. Kodni tekshirish
                    xato_matni = "Xato topilmadi"
                    try:
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    # 2. AI dan javob olish (Eng oddiy murojaat)
                    with st.spinner('AI bog\'lanmoqda...'):
                        try:
                            prompt = f"Kod: {kod}\nXato: {xato_matni}\nO'zbek tilida Sokratik savol ber."
                            # Hech qanday RequestOptions'larsiz oddiy chaqiruv
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI model bilan bog'lanishda muammo: {ai_err}")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ API Key kiriting!")
