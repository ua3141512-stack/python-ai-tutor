import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()

if api_key_input:
    try:
        genai.configure(api_key=api_key_input)
        
        # Mavjud modellarni tekshirish (Xatolikni aniqlash uchun)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Eng yaxshi modelni tanlash
        selected_model = None
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.0-pro']:
            if target in available_models:
                selected_model = target
                break
        
        if selected_model:
            model = genai.GenerativeModel(selected_model)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                kod = st.text_area("Python kodingizni kiriting:", height=300)
                if st.button("Tahlil qilish 🔍"):
                    xato_matni = "Xato yo'q"
                    try:
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    with st.spinner(f'{selected_model} bilan tahlil qilinmoqda...'):
                        try:
                            response = model.generate_content(f"Kod: {kod}\nXato: {xato_matni}\nO'zbekcha Sokratik savol ber.")
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI xatosi: {ai_err}")
        else:
            st.error("Hisobingizda birorta ham foydalanish mumkin bo'lgan model topilmadi.")
            st.write("Mavjud modellar:", available_models)
            
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ API Key kiriting!")
