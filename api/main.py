"""Optional FastAPI health endpoints for deployment diagnostics.

This module is not required for Streamlit execution but can be helpful when
hosting the project on platforms that expect an HTTP health probe.
"""
from __future__ import annotations

from fastapi import FastAPI

APP_VERSION = "0.1.0"

app = FastAPI(title="Healthy Meal Creator API", version=APP_VERSION)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return a simple status payload for uptime checks."""

    return {"status": "ok"}


@app.get("/version")
async def version() -> dict[str, str]:
    """Expose the app version for automated diagnostics."""

    return {"version": APP_VERSION}
