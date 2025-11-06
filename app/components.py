"""Reusable Streamlit UI components."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st

from services import paths


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

    st.json(json.loads(json.dumps(data)), expanded=expanded)


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

    days = plan.get("days") if isinstance(plan, dict) else None
    if not days:
        st.write(plan)
        return

    rows = []
    for day, meals in days.items():
        breakfast = meals.get("breakfast", "")
        lunch = meals.get("lunch", "")
        dinner = meals.get("dinner", "")
        rows.append({
            "Day": day,
            "Breakfast": breakfast,
            "Lunch": lunch,
            "Dinner": dinner,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


def render_env_table(keys: Iterable[str]) -> None:
    """Display environment variables in a masked manner."""

    data = []
    for key in keys:
        value = st.session_state.get(key) or st.secrets.get(key) or ""
        masked = "•" * 6 if value else ""
        data.append({"Key": key, "Configured": bool(value), "Value": masked})
    st.dataframe(pd.DataFrame(data))
