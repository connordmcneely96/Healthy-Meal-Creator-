from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components
from services import images

st.set_page_config(page_title="Image Studio", page_icon="🎨")
st.title("Image Studio")
st.write("Generate healthy meal visuals with OpenAI's image APIs.")

if not images.is_configured():
    st.warning("Configure your OPENAI_API_KEY in Settings to enable this tool.")

prompt = st.text_area(
    "Image prompt",
    value="A high-resolution photo of a balanced Mediterranean lunch platter",
    height=150,
)
size = st.selectbox("Image size", options=["256x256", "512x512", "1024x1024"], index=1)

if st.button("Generate image", disabled=not images.is_configured()):
    with st.spinner("Generating image..."):
        try:
            result = images.generate_image(prompt, size=size)
        except Exception as exc:  # pragma: no cover - network call
            st.error(str(exc))
            result = None
    if result:
        path = Path(result["path"])
        st.success(f"Image saved to {path}")
        st.image(str(path))
        st.download_button("Download", data=path.read_bytes(), file_name=path.name)

with st.expander("Recent images"):
    components.render_directory_listing(Path("data/dalle"))
