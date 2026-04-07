import streamlit as st
import google.generativeai as genai

# 1. Sahifa dizayni
st.set_page_config(page_title="AI Python Tutor", layout="wide")

st.title("🎓 Intellektual Python Repetitori")
st.info("Kodingizni tahlil qiling va sun'iy intellektdan metodik yordam oling.")

# 2. Sidebar - Sozlamalar
with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # .strip() kiritilgan bo'shliqlarni avtomatik o'chiradi
    api_key_input = st.text_input("Gemini API Key:", type="password").strip()
    st.markdown("---")
    st.write("Dasturchi: Jaloliddin")

# 3. Asosiy mantiq
if api_key_input:
    try:
        # API ni sozlash
        genai.configure(api_key=api_key_input)
        
        # Eng yangi model nomi
        model = genai.GenerativeModel('gemini-1.5-flash')

        col1, col2 = st.columns([1, 1])
        
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300, placeholder="Masalan: print('Salom')")
            tahlil_tugma = st.button("Tahlil qilish 🔍")

            if tahlil_tugma:
                if not kod.strip():
                    st.warning("Iltimos, avval kod yozing!")
                else:
                    # Kodni bajarib ko'rish
                    xato_matni = "Xato topilmadi (Muvaffaqiyatli)"
                    try:
                        # Kodni xavfsiz muhitda tekshirish
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    # AI dan tahlil so'rash
                    with st.spinner('AI o\'ylamoqda...'):
                        try:
                            prompt = f"Sen tajribali Python o'qituvchisisan. Talaba yozgan kod: {kod}\nKelib chiqqan xato: {xato_matni}\n\nVazifang: Talabaga xatoni to'g'ridan-to'g'ri aytma. Unga o'zbek tilida Sokratik uslubda (savollar orqali) xatosini topishga yordam ber."
                            response = model.generate_content(prompt)
                            
                            with col2:
                                st.subheader("🤖 AI Repetitor javobi:")
                                st.code(xato_matni, language="python")
                                st.success(response.text)
                        except Exception as ai_err:
                            st.error(f"AI bilan bog'lanishda xato: {ai_err}")
                            st.info("Eslatma: API kalitingiz to'g'riligini va internetni tekshiring.")
                            
    except Exception as general_err:
        st.error(f"Tizimda kutilmagan xato: {general_err}")
else:
    st.warning("⚠️ Davom etish uchun chap tomondagi menyuga Gemini API Key kiriting!")
