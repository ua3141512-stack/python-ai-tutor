import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Python Tutor", layout="wide", page_icon="🎓")

st.title("🎓 Intellektual Python Repetitori")
st.markdown("---")

with st.sidebar:
st.header("⚙️ Sozlamalar")
api_key_input = st.text_input("Groq API Keyni kiriting:", type="password").strip()
st.write("---")
st.info("Dasturchi: Jaloliddin")

if api_key_input:
try:
client = Groq(api_key=api_key_input)
col1, col2 = st.columns([1, 1])

else:
st.warning("⚠️ Groq API Keyni kiriting!")

st.markdown("---")
st.caption("© 2026 Python AI Tutor")
