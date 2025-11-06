"""Speech utilities for transcription and TTS using OpenAI."""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from typing import Dict

try:  # pragma: no cover - optional dependency for tests
    from openai import OpenAI
    from openai.error import OpenAIError
except ImportError:  # pragma: no cover - optional dependency for tests
    OpenAI = None  # type: ignore

    class OpenAIError(Exception):
        pass

from .paths import LOG_DIR, WHISPER_DIR, ensure_data_directories

TRANSCRIBE_MODEL = os.environ.get("OPENAI_TRANSCRIBE_MODEL", "whisper-1")
TTS_MODEL = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
DEFAULT_VOICE = os.environ.get("OPENAI_TTS_VOICE", "alloy")


def is_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY")) and OpenAI is not None


def _client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError(
            "OpenAI Python client is not installed. Install the 'openai' package."
        )
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OpenAI API key is not configured. Set OPENAI_API_KEY env variable."
        )
    return OpenAI(api_key=key)


def transcribe_audio(file_path: str | Path) -> Dict[str, str]:
    """Transcribe an audio file using the Whisper model."""

    ensure_data_directories()
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    try:
        client = _client()
        with file_path.open("rb") as audio:
            result = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=audio,
            )
    except OpenAIError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Transcription failed: {exc}") from exc

    transcript = result.text
    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    output_path = WHISPER_DIR / f"transcript_{timestamp}.txt"
    output_path.write_text(transcript, encoding="utf-8")

    return {"path": str(output_path), "text": transcript}


def text_to_speech(text: str, *, voice: str | None = None) -> Dict[str, str]:
    """Convert text to speech and save the audio file to disk."""

    ensure_data_directories()
    voice_name = voice or DEFAULT_VOICE
    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    output_path = LOG_DIR / f"tts_{timestamp}.mp3"

    try:
        client = _client()
        result = client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice_name,
            input=text,
        )
    except OpenAIError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Text-to-speech failed: {exc}") from exc

    output_path.write_bytes(result.read())
    return {"path": str(output_path), "voice": voice_name}


__all__ = ["transcribe_audio", "text_to_speech", "is_configured"]
