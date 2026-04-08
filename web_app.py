import streamlit as st
from groq import Groq

# Sahifa sozlamalari
st.set_page_config(page_title="AI Python Tutor", layout="wide")
st.title("🎓 Python Repetitori (Groq AI)")

with st.sidebar:
    st.header("⚙️ Sozlamalar")
    # Bu yerga gsk_... bilan boshlanadigan kalitni kiritasiz
    api_key_input = st.text_input("Groq API Key:", type="password").strip()
    st.write("---")
    st.write("Dasturchi: Jaloliddin")
    st.info("API kalitni console.groq.com dan oling.")

if api_key_input:
    try:
        # Groq mijozini sozlash
        client = Groq(api_key=api_key_input)

        col1, col2 = st.columns([1, 1])
        with col1:
            kod = st.text_area("Python kodingizni kiriting:", height=300, placeholder="print('Salom')")
            if st.button("Tahlil qilish 🔍"):
                if not kod.strip():
                    st.warning("Iltimos, avval kod yozing!")
                else:
                    # 1. Kodni oddiy tekshirish
                    xato_matni = "Kodda sintaktik xato topilmadi."
                    try:
                        exec(kod, {})
                    except Exception as e:
                        xato_matni = f"{type(e).__name__}: {str(e)}"
                    
                    # 2. AI dan javob olish
                    with st.spinner('AI tahlil qilmoqda...'):
                        try:
                            completion = client.chat.completions.create(
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "Sen o'zbek tilida gapiradigan mohir Python o'qituvchisisan. Talabaga xatoni darrov aytma, Sokratik usulda (savollar berish orqali) uni o'ylashga majbur qil va yordam ber."
                                    },
                                    {
                                        "role": "user",
                                        "content": f"Talaba kodi: {kod}\nNatija/Xato: {xato_matni}\nUnga o'zbek tilida yordam ber."
                                    }
                                ],
                                model="llama3-70b-8192", # Eng kuchli tekin model
                            )
                            
                            with col2:
                                st.subheader("🤖 AI javobi:")
                                st.success(completion.choices[0].message.content)
                        except Exception as ai_err:
                            st.error(f"AI bilan bog'lanishda xato: {ai_err}")
    except Exception as e:
        st.error(f"Tizim xatosi: {e}")
else:
    st.warning("⚠️ Davom etish uchun Groq API Keyni kiriting!")
