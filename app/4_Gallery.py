from __future__ import annotations

from pathlib import Path

import streamlit as st

from app import components
from services import paths

st.set_page_config(page_title="Artifact Gallery", page_icon="🗂️")
components.page_title(
    "Artifact Gallery",
    icon="🗂️",
    description="Browse everything the tools have generated in your data directory.",
)

sections = {
    "Meal plans": {
        "directory": paths.MEAL_PLAN_DIR,
        "kinds": {".md": "text", ".json": "text"},
        "columns": 2,
    },
    "Images": {
        "directory": paths.DALLE_DIR,
        "kinds": {".png": "image", ".jpg": "image", ".jpeg": "image"},
        "columns": 3,
    },
    "Transcripts": {
        "directory": paths.WHISPER_DIR,
        "kinds": {".txt": "text"},
        "columns": 2,
    },
    "Audio & summaries": {
        "directory": paths.LOG_DIR,
        "kinds": {".mp3": "audio", ".md": "text"},
        "columns": 2,
    },
}

counts = []
for label, config in sections.items():
    directory: Path = config["directory"]
    count = sum(1 for path in directory.rglob("*") if path.is_file())
    counts.append((label, str(count)))

components.stat_pills(counts)

for label, config in sections.items():
    directory: Path = config["directory"]
    st.subheader(label)
    files = sorted(
        (path for path in directory.rglob("*") if path.is_file()),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )[:9]
    media_items = []
    for file in files:
        kind = config["kinds"].get(file.suffix.lower(), "text")
        media_items.append(components.MediaItem(path=file, kind=kind, caption=file.name))
    components.media_grid(media_items, columns=config.get("columns", 3))

    with st.expander(f"All files in {label}"):
        components.render_directory_listing(directory)
