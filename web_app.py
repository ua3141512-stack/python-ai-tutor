import streamlit as st
import google.generativeai as genai

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # Yangi API keyni (AIzaSyC...) probellarsiz kiriting
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        # API ni sozlash
        genai.configure(api_key=api_key_input)
        
        # ENG BARQAROR MODEL: 'gemini-pro'
        # Bu model barcha kutubxona versiyalarida mavjud
        model = genai.GenerativeModel('gemini-pro')

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
                    
                    # 2. AI dan javob olish
                    with st.spinner('AI bilan bog\'lanmoqda...'):
                        try:
                            prompt = f"Talaba kodi: {kod}\nXato: {xato_matni}\nO'zbek tilida Sokratik savol ber."
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI model bilan bog'lanishda muammo: {ai_err}")
                            st.info("Eslatma: Google AI Studio'da 'Gemini API' xizmati yoqilganini (Enabled) tekshiring.")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ Yangi API Keyni (AIzaSyC...) kiriting!")
