from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests
import streamlit as st

from app import components
from services import paths, speech

st.set_page_config(page_title="Speech Lab", page_icon="🎙️")
components.page_title(
    "Speech Lab",
    icon="🎙️",
    description="Transcribe, translate, summarise, and synthesise audio with OpenAI.",
)

if not speech.is_configured():
    st.warning("Add your OpenAI API key in Settings to unlock speech features.")

st.subheader("Transcribe & translate")
with st.form("transcription-form"):
    uploaded_audio = st.file_uploader(
        "Upload audio", type=["mp3", "wav", "m4a", "aac", "ogg"], accept_multiple_files=False
    )
    audio_url = st.text_input("Or fetch from URL", placeholder="https://example.com/audio.mp3")
    translate = st.checkbox("Translate to English", value=True)
    submitted_transcribe = st.form_submit_button(
        "Process audio", type="primary", disabled=not speech.is_configured()
    )

transcript_result = None
summary_result = None
source_audio_path: Path | None = None

if submitted_transcribe:
    if not uploaded_audio and not audio_url:
        st.error("Provide an upload or URL to transcribe.")
    else:
        try:
            if uploaded_audio:
                suffix = Path(uploaded_audio.name).suffix or ".mp3"
                source_audio_path = paths.build_artifact_path(
                    paths.LOG_DIR, f"upload-{Path(uploaded_audio.name).stem}", ext=suffix
                )
                source_audio_path.write_bytes(uploaded_audio.getbuffer())
            else:
                response = requests.get(audio_url, timeout=30)
                response.raise_for_status()
                guessed_name = Path(urlparse(audio_url).path).name or "remote-audio"
                suffix = Path(guessed_name).suffix or ".mp3"
                source_audio_path = paths.build_artifact_path(
                    paths.LOG_DIR, f"remote-{Path(guessed_name).stem}", ext=suffix
                )
                source_audio_path.write_bytes(response.content)
        except Exception as exc:  # pragma: no cover - network interaction
            st.error(f"Failed to load audio: {exc}")
            source_audio_path = None

        if source_audio_path:
            st.audio(str(source_audio_path))
            with st.spinner("Contacting Whisper..."):
                try:
                    transcript_result = speech.transcribe_audio(
                        source_audio_path, translate=translate
                    )
                except Exception as exc:  # pragma: no cover - network call
                    st.error(str(exc))
                    transcript_result = None

            if transcript_result and transcript_result.get("text"):
                st.success("Transcript ready")
                transcript_text = transcript_result["text"]
                components.stat_pills(
                    [
                        ("Translated", "Yes" if translate else "No"),
                        ("Length", f"{len(transcript_text.split())} words"),
                    ]
                )
                st.text_area("Transcript", value=transcript_text, height=200)
                st.download_button(
                    "Download transcript",
                    data=transcript_text,
                    file_name=Path(transcript_result["path"]).name,
                    type="secondary",
                )

                with st.spinner("Summarising transcript..."):
                    try:
                        summary_result = speech.summarize_text(transcript_text)
                    except Exception as exc:  # pragma: no cover - network call
                        st.error(str(exc))
                        summary_result = None

                if summary_result and summary_result.get("summary"):
                    st.markdown("### Summary")
                    st.markdown(summary_result["summary"])
                    st.caption("Summary stored in data/logs for reference.")

st.divider()

st.subheader("Text to speech")
with st.form("tts-form"):
    tts_text = st.text_area(
        "Narration text",
        value="Remember to hydrate and include colourful vegetables in your meals.",
        height=120,
    )
    voice = st.text_input("Voice", value="alloy")
    submitted_tts = st.form_submit_button(
        "Synthesise audio", type="primary", disabled=not speech.is_configured()
    )

tts_result = None
if submitted_tts:
    try:
        tts_result = speech.text_to_speech(tts_text, voice=voice)
    except Exception as exc:  # pragma: no cover - network call
        st.error(str(exc))
        tts_result = None

    if tts_result:
        audio_path = Path(tts_result["path"])
        components.stat_pills([("Voice", voice), ("Format", "MP3")])
        st.audio(str(audio_path))
        st.download_button(
            "Download speech",
            data=audio_path.read_bytes(),
            file_name=audio_path.name,
            type="secondary",
        )

with st.expander("Recent transcripts"):
    components.render_directory_listing(paths.WHISPER_DIR)

with st.expander("Recent audio logs"):
    components.render_directory_listing(paths.LOG_DIR)
