from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components
from services import paths

st.set_page_config(page_title="Artifact Gallery", page_icon="🗂️")
st.title("Artifact Gallery")
st.write("Browse all generated assets stored under the data directory.")

for label, directory in {
    "Meal plans": paths.MEAL_PLAN_DIR,
    "Images": paths.DALLE_DIR,
    "Transcripts": paths.WHISPER_DIR,
    "Logs": paths.LOG_DIR,
}.items():
    st.subheader(label)
    components.render_directory_listing(directory)
