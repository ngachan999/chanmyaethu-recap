import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
import re

st.set_page_config(page_title="chanmyaethu - YT to Movie Recap")
st.title("🎬 chanmyaethu")

with st.sidebar:
    api_key = st.text_input("Gemini API Key ထည့်ပါ:", type="password")

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

yt_url = st.text_input("YouTube Video Link ကို ဒီမှာထည့်ပါ:")
voice_choice = st.selectbox("အသံရွေးပါ:", ["Female (Nilar)", "Male (Thiha)"])
voice_id = "my-MM-NilarNeural" if "Female" in voice_choice else "my-MM-ThihaNeural"

if st.button("Generate Now"):
    vid = get_video_id(yt_url)
    if not api_key: st.error("API Key ထည့်ပါ")
    elif not vid: st.warning("Link မှန်အောင်ထည့်ပါ")
    else:
        try:
            # 1. English Transcript ယူခြင်း
            with st.spinner("English Transcript ဆွဲယူနေသည်..."):
                data = YouTubeTranscriptApi.get_transcript(vid)
                eng_text = " ".join([i['text'] for i in data])
                st.success("✅ English Transcript ရပါပြီ")

            # 2. Gemini နဲ့ မြန်မာလို Recap လုပ်ခြင်း
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            with st.spinner("မြန်မာလို Recap ရေးနေသည်..."):
                prompt = f"ဒီ English transcript ကိုအခြေခံပြီး စိတ်လှုပ်ရှားစရာ မြန်မာ Movie Recap ရေးပေးပါ: {eng_text}"
                response = model.generate_content(prompt)
                burmese_script = response.text
                st.write(burmese_script)

            # 3. အသံဖိုင်ထုတ်ခြင်း
            with st.spinner("အသံဖိုင် လုပ်နေသည်..."):
                asyncio.run(edge_tts.Communicate(burmese_script, voice_id).save("recap.mp3"))
                st.audio("recap.mp3")
                st.download_button("📥 အသံဖိုင်ဒေါင်းရန်", open("recap.mp3", "rb"), "recap.mp3")

        except Exception as e:
            st.error(f"Error: {e}")
            
