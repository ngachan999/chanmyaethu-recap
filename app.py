import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio

st.set_page_config(page_title="chanmyaethu - Movie Recap")
st.title("🎬 chanmyaethu")
st.info("AI Movie Recap Script & Audio Generator")

api_key = st.sidebar.text_input("Gemini API Key ထည့်ပါ:", type="password")
transcript = st.text_area("YouTube Transcript ထည့်ပါ:", height=200)

col1, col2 = st.columns(2)
with col1:
    voice_choice = st.selectbox("အသံရွေးပါ:", ["Female (Nilar)", "Male (Thiha)"])
    voice_id = "my-MM-NilarNeural" if "Female" in voice_choice else "my-MM-ThihaNeural"

async def generate_audio(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

if st.button("Generate Now"):
    if not api_key:
        st.error("Sidebar တွင် API Key အရင်ထည့်ပါ!")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        with st.spinner("AI Script ရေးနေသည်..."):
            response = model.generate_content(f"ဒီ transcript ကို စိတ်လှုပ်ရှားစရာ မြန်မာလို movie recap အဖြစ် ပြန်ရေးပါ: {transcript}")
            st.write(response.text)
            audio_file = "recap.mp3"
            asyncio.run(generate_audio(response.text, voice_id, audio_file))
            st.audio(open(audio_file, "rb").read(), format="audio/mp3")
            st.download_button("📥 အသံဖိုင်ဒေါင်းလုဒ်ဆွဲရန်", open(audio_file, "rb"), "recap.mp3")
          
