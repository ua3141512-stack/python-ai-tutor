import streamlit as st
import google.generativeai as genai

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")

st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # Yangi API keyni shu yerga kiritasiz
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.markdown("---")
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        genai.configure(api_key=api_key_input)
        
        # Eng ishonchli va yangi model nomi
        model = genai.GenerativeModel('gemini-1.5-flash')

        col1, col2 = st.columns([1, 1])
        
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300, placeholder="print('Salom')")
            if st.button("Tahlil qilish 🔍"):
                if not kod.strip():
                    st.warning("Iltimos, avval kod yozing!")
                else:
                    # 1. Kodni bajarib ko'rish
                    xato_matni = "Xato topilmadi"
                    try:
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    # 2. AI dan javob olish
                    with st.spinner('AI bog\'lanmoqda...'):
                        try:
                            prompt = f"Talaba kodi: {kod}\nXato: {xato_matni}\n\nO'zbek tilida Sokratik savol ber."
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.code(xato_matni, language="python")
                                st.success(response.text)
                        except Exception as ai_err:
                            # Agar model nomi bilan muammo bo'lsa, xatoni ko'rsatadi
                            st.error(f"AI bilan bog'lanishda xato: {ai_err}")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ Davom etish uchun yangi API Keyni (AIzaSyC...) kiriting!")
