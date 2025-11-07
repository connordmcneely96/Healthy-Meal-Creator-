"""Streamlit playground for local demos."""

import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="Unified AI Lab • Streamlit",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Unified AI Lab – OpenAI Smoke Test")
st.caption(
    "This Streamlit app is intended for local development and GitHub Codespaces demos."
)

api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.warning(
        "Set OPENAI_API_KEY in a local .env file or Codespaces secret to enable OpenAI calls.",
        icon="⚠️",
    )
else:
    client = OpenAI(api_key=api_key)

    with st.form("prompt-form", clear_on_submit=False):
        prompt = st.text_area(
            "Prompt",
            value="Say hello from Streamlit!",
            help="Your text will be sent to OpenAI's Responses API",
        )
        submitted = st.form_submit_button("Generate response")

    if submitted:
        with st.spinner("Contacting OpenAI..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=prompt,
                    max_output_tokens=200,
                )
                st.success("Model response")
                st.write(response.output_text)
            except Exception as exc:  # pragma: no cover - surface API errors to UI
                st.error(f"OpenAI request failed: {exc}")

st.divider()
st.markdown(
    "Need an API key? Visit [platform.openai.com](https://platform.openai.com/)."
)
