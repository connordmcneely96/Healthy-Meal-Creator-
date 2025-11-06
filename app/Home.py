from __future__ import annotations

import platform
import socket

import streamlit as st

from app import components
from services import gpt, images, paths, speech

st.set_page_config(page_title="Healthy Meal Creator", page_icon="🥗", layout="wide")

st.title("🥗 Healthy Meal Creator — Diagnostics")
st.markdown(
    """Use this dashboard to verify your environment before exploring the tools.
    The checks below run on every refresh so you can immediately validate
    configuration changes."""
)

with st.expander("Environment info", expanded=False):
    st.write({
        "Python": platform.python_version(),
        "Hostname": socket.gethostname(),
        "OpenAI client": st.session_state.get("openai_client_version", "1.13+"),
    })

st.subheader("Health checks")

components.render_status_badge(
    "OpenAI API Key",
    ok=gpt.is_configured(),
    help_text="Set OPENAI_API_KEY in your environment or session state.",
)
components.render_status_badge(
    "Image service configured",
    ok=images.is_configured(),
    help_text="Required for DALL·E image generation.",
)
components.render_status_badge(
    "Speech service configured",
    ok=speech.is_configured(),
    help_text="Needed for Whisper transcription and TTS.",
)

components.render_status_badge(
    "Data directories",
    ok=all(path.exists() for path in (paths.MEAL_PLAN_DIR, paths.DALLE_DIR, paths.WHISPER_DIR)),
    help_text=f"Artifacts stored in {paths.DATA_ROOT}",
)

with st.expander("Directory overview"):
    st.write({
        "Meal plans": str(paths.MEAL_PLAN_DIR),
        "Images": str(paths.DALLE_DIR),
        "Transcripts": str(paths.WHISPER_DIR),
        "Logs": str(paths.LOG_DIR),
    })
