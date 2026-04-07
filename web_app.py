import streamlit as st
import google.generativeai as genai

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # YANGI API KEYNI SHU YERGA QO'YING
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        # API ni sozlash
        genai.configure(api_key=api_key_input)
        
        # SIZNING HISOBINGIZDA MAVJUD BO'LGAN ANIQ MODEL:
        # 'models/' prefiksi bilan yozish xatolikni oldini oladi
        model = genai.GenerativeModel('models/gemini-1.5-flash-8b')

        col1, col2 = st.columns([1, 1])
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300, placeholder="Masalan: print('Salom')")
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
                    with st.spinner('Gemini 2.0 tahlil qilmoqda...'):
                        try:
                            prompt = f"Talaba kodi: {kod}\nXato: {xato_matni}\n\nO'zbek tilida Sokratik savol ber."
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.code(xato_matni, language="python")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI bilan bog'lanishda xato: {ai_err}")
                            st.info("Maslahat: Agar 'Quota exceeded' chiqsa, 5 daqiqa kuting.")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ Davom etish uchun yangi API Keyni kiriting!")
