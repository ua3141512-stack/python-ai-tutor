import streamlit as st
from groq import Groq

# 1. Sahifa sozlamalari va Dizayn
st.set_page_config(page_title="AI Python Mentor", layout="wide", page_icon="🤖")

# Maxfiy kalitni olish
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = None

# CSS orqali chat ko'rinishini chiroyli qilamiz
st.markdown("""
    <style>
    .stChatFloatingInputContainer {padding-bottom: 20px;}
    .reportview-container { background: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Professional AI Python Mentor")
st.caption("Magistratura darajasidagi intellektual yordamchi")

# 2. Session State - Suhbat tarixini saqlash uchun
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar - Funksiyalar
with st.sidebar:
    st.header("⚙️ Boshqaruv")
    if st.button("Suhbatni tozalash 🗑️"):
        st.session_state.messages = []
        st.rerun()
    
    st.write("---")
    st.info(f"Dasturchi: Jaloliddin\nStatus: Magistr/Researcher")
    if not api_key:
        st.error("API Key topilmadi!")

# 4. Asosiy Chat Interfeysi
if api_key:
    client = Groq(api_key=api_key)

    # Avvalgi xabarlarni ekranga chiqarish
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Foydalanuvchi kiritishi
    if prompt := st.chat_input("Python bo'yicha savol bering yoki kodingizni tashlang..."):
        
        # Foydalanuvchi xabarini saqlash
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI javobini generatsiya qilish
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Tizimga "shaxsiyat" berish (System Prompt)
                system_instruction = {
                    "role": "system", 
                    "content": """Sen magistr darajasidagi mohir Python dasturchisisan. 
                    Sening vazifang foydalanuvchi bilan xuddi professional hamkasbdek gaplashish.
                    Agar foydalanuvchi kod tashlasa, uni chuqur tahlil qil (Time/Space complexity, PEP8, xavfsizlik).
                    Suhbat davomida avvalgi aytilgan gaplarni eslab qol va shunga qarab javob ber.
                    Javoblaring aniq, lo'nda va o'zbek tilida bo'lsin."""
                }
                
                # Chat tarixini AI ga yuborish
                messages_for_api = [system_instruction] + st.session_state.messages
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_for_api,
                    stream=False # Magistrlik ishi uchun barqarorlik muhim
                )
                
                full_response = completion.choices[0].message.content
                message_placeholder.markdown(full_response)
                
                # AI javobini tarixga saqlash
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Xatolik yuz berdi: {e}")

else:
    st.warning("Iltimos, Secrets bo'limiga GROQ_API_KEY ni qo'shing.")
