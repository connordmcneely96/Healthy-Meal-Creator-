from __future__ import annotations

import os

import streamlit as st

from app import components

st.set_page_config(page_title="Settings", page_icon="⚙️")
st.title("Settings")
st.write(
    "Configure API keys and model defaults. Values are stored in Streamlit"
    " session state only and never persisted to disk."
)

OPENAI_KEY = "OPENAI_API_KEY"

if OPENAI_KEY not in st.session_state:
    st.session_state[OPENAI_KEY] = os.environ.get(OPENAI_KEY, "")

with st.form("settings-form"):
    api_key = st.text_input("OpenAI API Key", value=st.session_state[OPENAI_KEY], type="password")
    default_model = st.text_input(
        "Default chat model",
        value=os.environ.get("OPENAI_DEFAULT_CHAT_MODEL", "gpt-3.5-turbo"),
    )
    submitted = st.form_submit_button("Save settings", type="primary")

    if submitted:
        st.session_state[OPENAI_KEY] = api_key
        if api_key:
            os.environ[OPENAI_KEY] = api_key
        os.environ["OPENAI_DEFAULT_CHAT_MODEL"] = default_model
        st.success("Settings updated for this session.")

st.subheader("Current configuration")
components.render_env_table([OPENAI_KEY, "OPENAI_DEFAULT_CHAT_MODEL"])

st.caption("Provide environment variables via .env or deployment secrets for production.")
