from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components
from services import images, paths

st.set_page_config(page_title="Image Studio", page_icon="🎨")
components.page_title(
    "Image Studio",
    icon="🎨",
    description="Craft fresh visuals or remix existing assets with GPT-Image-1.",
)

if not images.is_configured():
    st.warning("Add your OpenAI API key in Settings to enable image features.")

with st.form("image-form"):
    prompt = st.text_area(
        "Prompt",
        value="A vibrant flat-lay of a balanced Mediterranean-inspired lunch",
        height=140,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        style = st.selectbox(
            "Style",
            options=[
                "Photographic",
                "Illustrative",
                "Watercolour",
                "3D Render",
                "Sketch",
            ],
            index=0,
        )
    with col2:
        size = st.selectbox("Size", options=["256x256", "512x512", "1024x1024"], index=1)
    with col3:
        n_images = st.slider("Images", min_value=1, max_value=4, value=2)

    edit_image = st.file_uploader("Edit existing image (optional)", type=["png", "jpg", "jpeg"])
    mask_image = st.file_uploader(
        "Mask (optional, transparent PNG)",
        type=["png"],
        help="Transparent areas reveal edits; leave empty for whole-image edits.",
    )

    submitted = st.form_submit_button(
        "Create visuals", type="primary", disabled=not images.is_configured()
    )

if submitted:
    saved_paths: list[str] = []
    try:
        if edit_image:
            uploaded_suffix = Path(edit_image.name).suffix or ".png"
            base_path = paths.build_artifact_path(
                paths.LOG_DIR, f"edit-source-{Path(edit_image.name).stem}", ext=uploaded_suffix
            )
            base_path.write_bytes(edit_image.getbuffer())
            mask_path = None
            if mask_image:
                mask_path = paths.build_artifact_path(
                    paths.LOG_DIR, f"mask-{Path(mask_image.name).stem}", ext=".png"
                )
                mask_path.write_bytes(mask_image.getbuffer())
            result = images.edit_image(
                base_path,
                prompt=prompt,
                mask_path=mask_path,
                size=size,
                n=n_images,
                style=style,
            )
        else:
            result = images.generate_image(
                prompt,
                size=size,
                n=n_images,
                style=style,
            )
        saved_paths = [str(path) for path in result.get("paths", [])]
    except Exception as exc:  # pragma: no cover - network call
        st.error(str(exc))
        result = None

    if result and saved_paths:
        components.stat_pills(
            [
                ("Images", str(len(saved_paths))),
                ("Size", size),
                ("Style", style),
            ]
        )
        media_items = [
            components.MediaItem(path=Path(path), caption=Path(path).name)
            for path in saved_paths
        ]
        components.media_grid(media_items, columns=2 if len(saved_paths) <= 4 else 3)

        for path in saved_paths:
            file_path = Path(path)
            st.download_button(
                f"Download {file_path.name}",
                data=file_path.read_bytes(),
                file_name=file_path.name,
                type="secondary",
            )
        components.render_json_block(result)
        st.caption("Images are stored in the data/dalle directory.")
if not submitted:
    st.info("Submit the form above to generate new visuals or edit an upload.")

with st.expander("Recent images"):
    components.render_directory_listing(paths.DALLE_DIR)
