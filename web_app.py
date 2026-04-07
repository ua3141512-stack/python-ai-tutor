import streamlit as st
import google.generativeai as genai

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")

st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # API keyni kiritish (probellarsiz)
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.markdown("---")
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        # API ni sozlash
        genai.configure(api_key=api_key_input)
        
        # MODEL NOMI: 'models/gemini-1.5-flash-latest' 
        # Bu format xatoliklarni oldini olish uchun eng ishonchlisi
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

        col1, col2 = st.columns([1, 1])
        
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300, placeholder="Masalan: print('Salom')")
            if st.button("Tahlil qilish 🔍"):
                if not kod.strip():
                    st.warning("Iltimos, avval kod yozing!")
                else:
                    # Kodni tekshirish
                    xato_matni = "Xato topilmadi"
                    try:
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    with st.spinner('AI javob tayyorlamoqda...'):
                        try:
                            # Prompt yozish
                            prompt = f"Talaba kodi: {kod}\nXato: {xato_matni}\n\nO'zbek tilida Sokratik savol ber."
                            
                            # Generatsiya qilish
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.code(xato_matni, language="python")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI model bilan bog'lanishda xato: {ai_err}")
                            st.info("Maslahat: Google AI Studio'da API kalitingiz 'Active' ekanligini tekshiring.")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ Davom etish uchun API Key kiriting!")
