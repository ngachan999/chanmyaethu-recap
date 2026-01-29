import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
import re

st.set_page_config(page_title="chanmyaethu - YouTube to Movie Recap")
st.title("🎬 chanmyaethu Movie Recap")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key ထည့်ပါ:", type="password")

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

yt_url = st.text_input("YouTube Video Link ကို ဒီမှာထည့်ပါ:")
voice_choice = st.selectbox("အသံရွေးပါ:", ["Female (Nilar)", "Male (Thiha)"])
voice_id = "my-MM-NilarNeural" if "Female" in voice_choice else "my-MM-ThihaNeural"

async def generate_audio(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await asyncio.sleep(1) # ခေတ္တစောင့်ဆိုင်းရန်
    await communicate.save(filename)

if st.button("Generate Now"):
    video_id = get_video_id(yt_url)
    if not api_key: st.error("Sidebar တွင် API Key ထည့်ပါ")
    elif not video_id: st.warning("Link မှန်အောင်ထည့်ပါ")
    else:
        try:
            # 1. Transcript ဆွဲယူခြင်း (Manual ရော Auto ပါ ရှာဖွေရန်)
            with st.spinner("စာသားများ ဆွဲယူနေသည်..."):
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                # English (Manual သို့မဟုတ် Auto) ကို အရင်ရှာမည်
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    transcript = transcript_list.find_generated_transcript(['en'])
                
                data = transcript.fetch()
                full_text = " ".join([t['text'] for t in data])
                st.success("✅ English Transcript ရရှိပါပြီ")

            # 2. Gemini နှင့် Movie Recap ရေးခြင်း
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            with st.spinner("မြန်မာလို Recap Script ရေးနေသည်..."):
                prompt = f"ဒီ English transcript ကိုအခြေခံပြီး စိတ်လှုပ်ရှားစရာ မြန်မာ Movie Recap script တစ်ခုရေးပေးပါ: \n\n {full_text}"
                response = model.generate_content(prompt)
                burmese_script = response.text
                st.subheader("📝 မြန်မာ Movie Recap Script")
                st.write(burmese_script)

            # 3. အသံဖိုင်ထုတ်ခြင်း
            with st.spinner("အသံဖိုင် ဖန်တီးနေသည်..."):
                audio_file = "recap.mp3"
                asyncio.run(generate_audio(burmese_script, voice_id, audio_file))
                st.audio(open(audio_file, "rb").read())
                st.download_button("📥 အသံဖိုင်ဒေါင်းရန်", open(audio_file, "rb"), "recap.mp3")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("ဗီဒီယိုတွင် English Caption လုံးဝ မပါဝင်သောကြောင့် ဖြစ်နိုင်ပါသည်။")

