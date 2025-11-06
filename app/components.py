"""Reusable Streamlit UI components."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import pandas as pd
import streamlit as st

from services import paths


@dataclass(frozen=True)
class MediaItem:
    """Represents an element that can be rendered within a gallery grid."""

    path: Path | None = None
    kind: str = "image"  # image, audio, text
    caption: str | None = None
    render: Callable[[], None] | None = None


def page_title(title: str, icon: str | None = None, description: str | None = None) -> None:
    """Render a consistent page header used across the app."""

    title_text = f"{icon} {title}" if icon else title
    st.title(title_text)
    if description:
        st.caption(description)


def stat_pills(items: Sequence[tuple[str, str]]) -> None:
    """Display compact stat blocks for quick facts."""

    if not items:
        return
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        with column:
            st.metric(label=label, value=value)


def media_grid(items: Iterable[MediaItem | Callable[[], None]], *, columns: int = 3) -> None:
    """Render a responsive grid of media elements."""

    item_list = list(items)
    if not item_list:
        st.info("Nothing to show yet. Generate some artifacts to populate the gallery.")
        return

    columns = max(1, columns)
    col_objects = st.columns(columns)
    for index, item in enumerate(item_list):
        column = col_objects[index % columns]
        with column:
            if callable(item):
                item()
                continue
            if item.path and item.kind == "image":
                st.image(str(item.path), caption=item.caption, use_column_width=True)
            elif item.path and item.kind == "audio":
                if item.caption:
                    st.markdown(f"**{item.caption}**")
                st.audio(str(item.path))
            elif item.path and item.kind == "text":
                text = Path(item.path).read_text(encoding="utf-8")
                if item.caption:
                    st.markdown(f"**{item.caption}**")
                st.write(text)
            elif item.render:
                item.render()
            else:
                st.write(item)


def render_status_badge(label: str, *, ok: bool, help_text: str | None = None) -> None:
    """Render a colour coded status indicator."""

    color = "green" if ok else "red"
    icon = "✅" if ok else "⚠️"
    with st.container(border=True):
        st.markdown(f"**{icon} {label}**")
        st.markdown(f":{color}[{'Healthy' if ok else 'Attention needed'}]")
        if help_text:
            st.caption(help_text)


def render_json_block(data: dict | list, *, expanded: bool = False) -> None:
    """Pretty-print data as JSON."""

    st.json(data, expanded=expanded)


def render_directory_listing(directory: Path, *, limit: int = 200) -> None:
    """Render files within a directory."""

    files = sorted(directory.glob("**/*"))[:limit]
    if not files:
        st.info("No files found yet. Generate some content to populate the gallery.")
        return

    for file in files:
        if file.is_dir():
            continue
        rel = file.relative_to(paths.DATA_ROOT)
        st.write(f"`{rel}` — {file.stat().st_size} bytes")


def render_meal_plan_table(plan: dict) -> None:
    """Render a meal plan dictionary as a table when possible."""

    days = plan.get("meals") or plan.get("days") if isinstance(plan, dict) else None
    if not days:
        st.write(plan)
        return

    rows = []
    for day, meals in days.items():
        if isinstance(meals, dict):
            rows.append({
                "Day": day,
                "Breakfast": meals.get("breakfast", ""),
                "Lunch": meals.get("lunch", ""),
                "Dinner": meals.get("dinner", ""),
                "Snacks": meals.get("snacks", ""),
            })
    if not rows:
        st.write(plan)
        return

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


def render_env_table(keys: Iterable[str]) -> None:
    """Display environment variables in a masked manner."""

    data = []
    secrets_obj = getattr(st, "secrets", None)
    for key in keys:
        secret_value = None
        if secrets_obj is not None:
            try:
                secret_value = secrets_obj.get(key)
            except Exception:
                secret_value = None
        value = st.session_state.get(key) or secret_value or ""
        masked = "•" * 6 if value else ""
        data.append({"Key": key, "Configured": bool(value), "Value": masked})
    st.dataframe(pd.DataFrame(data))


__all__ = [
    "MediaItem",
    "page_title",
    "stat_pills",
    "media_grid",
    "render_status_badge",
    "render_json_block",
    "render_directory_listing",
    "render_meal_plan_table",
    "render_env_table",
]
