from __future__ import annotations

import os

import streamlit as st

from app import components

st.set_page_config(page_title="Settings", page_icon="⚙️")
components.page_title(
    "Settings",
    icon="⚙️",
    description="Manage API credentials and tune default model options.",
)

OPENAI_KEY = "OPENAI_API_KEY"
DEFAULT_CHAT_MODEL_KEY = "OPENAI_DEFAULT_CHAT_MODEL"
DEFAULT_IMAGE_SIZE_KEY = "OPENAI_IMAGE_SIZE"
DEFAULT_TTS_VOICE_KEY = "OPENAI_TTS_VOICE"

if OPENAI_KEY not in st.session_state:
    st.session_state[OPENAI_KEY] = os.environ.get(OPENAI_KEY, "")

with st.form("settings-form"):
    api_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state[OPENAI_KEY],
        type="password",
        help="Stored in session only. Use deployment secrets for production.",
    )
    chat_model = st.text_input(
        "Default chat model",
        value=os.environ.get(DEFAULT_CHAT_MODEL_KEY, "gpt-4o-mini"),
        help="Applied to meal planning and summarisation calls.",
    )
    image_size = st.selectbox(
        "Default image size",
        options=["256x256", "512x512", "1024x1024"],
        index=["256x256", "512x512", "1024x1024"].index(
            os.environ.get(DEFAULT_IMAGE_SIZE_KEY, "512x512")
            if os.environ.get(DEFAULT_IMAGE_SIZE_KEY, "512x512") in {"256x256", "512x512", "1024x1024"}
            else "512x512"
        ),
    )
    voice = st.text_input(
        "Preferred TTS voice",
        value=os.environ.get(DEFAULT_TTS_VOICE_KEY, "alloy"),
    )
    submitted = st.form_submit_button("Save settings", type="primary")

if submitted:
    st.session_state[OPENAI_KEY] = api_key
    if api_key:
        os.environ[OPENAI_KEY] = api_key
    os.environ[DEFAULT_CHAT_MODEL_KEY] = chat_model
    os.environ[DEFAULT_IMAGE_SIZE_KEY] = image_size
    os.environ[DEFAULT_TTS_VOICE_KEY] = voice
    st.success("Session settings updated.")

components.stat_pills(
    [
        ("API configured", "Yes" if st.session_state.get(OPENAI_KEY) else "No"),
        ("Chat model", os.environ.get(DEFAULT_CHAT_MODEL_KEY, "gpt-4o-mini")),
        ("Image size", os.environ.get(DEFAULT_IMAGE_SIZE_KEY, "512x512")),
    ]
)

components.render_env_table(
    [OPENAI_KEY, DEFAULT_CHAT_MODEL_KEY, DEFAULT_IMAGE_SIZE_KEY, DEFAULT_TTS_VOICE_KEY]
)

st.caption(
    "Environment variables in a .env file or deployment secrets override these session settings."
)
