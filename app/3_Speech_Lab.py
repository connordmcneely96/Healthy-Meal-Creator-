from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components
from services import speech

st.set_page_config(page_title="Speech Lab", page_icon="🎙️")
st.title("Speech Lab")
st.write("Transcribe audio or create spoken meal tips with OpenAI.")

if not speech.is_configured():
    st.warning("Configure your OPENAI_API_KEY in Settings to enable this tool.")

st.header("Transcribe audio")
upload = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a"], accept_multiple_files=False)

if upload and speech.is_configured():
    temp_path = Path("data/logs") / upload.name
    temp_path.write_bytes(upload.getbuffer())
    with st.spinner("Transcribing..."):
        try:
            result = speech.transcribe_audio(temp_path)
        except Exception as exc:  # pragma: no cover - network call
            st.error(str(exc))
            result = None
    if result:
        st.success("Transcription saved")
        transcript_path = Path(result["path"])
        st.write(transcript_path.read_text())
        st.download_button(
            "Download transcript",
            data=transcript_path.read_text(),
            file_name=transcript_path.name,
        )

st.header("Text to speech")
text = st.text_area("Text to convert", value="Remember to drink water with every meal!", height=100)
voice = st.text_input("Voice", value="alloy")

if st.button("Generate speech", disabled=not speech.is_configured()):
    with st.spinner("Generating speech..."):
        try:
            result = speech.text_to_speech(text, voice=voice)
        except Exception as exc:  # pragma: no cover - network call
            st.error(str(exc))
            result = None
    if result:
        audio_path = Path(result["path"])
        st.audio(str(audio_path))
        st.download_button(
            "Download audio", data=audio_path.read_bytes(), file_name=audio_path.name
        )

with st.expander("Recent transcripts"):
    components.render_directory_listing(Path("data/whisper"))
