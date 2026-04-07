import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Intellektual Python Repetitori")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # YANGI KALITNI SHU YERGA QO'YASIZ
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.write("Dasturchi: Jaloliddin")

if api_key_input:
    try:
        genai.configure(api_key=api_key_input)
        
        # MODELNI TANLASH (Eng barqaror 1.5-flash versiyasi)
        # Bu modelda limitlar ko'proq va u tezroq ishlaydi
        model = genai.GenerativeModel('gemini-1.5-flash')

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
                    
                    with st.spinner('AI tahlil qilmoqda...'):
                        try:
                            prompt = f"Talaba kodi: {kod}\nXato: {xato_matni}\nO'zbek tilida Sokratik savol ber."
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.success(response.text)
                        except Exception as ai_err:
                            if "429" in str(ai_err):
                                st.error("Bu kalitning limiti tugadi. Iltimos, boshqa yangi API kalit kiriting.")
                            else:
                                st.error(f"Xato: {ai_err}")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ Yangi API Key kiriting!")
