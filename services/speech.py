"""Speech utilities for transcription, translation, summarisation, and TTS."""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict

try:  # pragma: no cover - optional dependency for tests
    from openai import OpenAI
    from openai.error import OpenAIError
except ImportError:  # pragma: no cover - optional dependency for tests
    OpenAI = None  # type: ignore

    class OpenAIError(Exception):
        pass

from .paths import LOG_DIR, WHISPER_DIR, build_artifact_path

TRANSCRIBE_MODEL = os.environ.get("OPENAI_TRANSCRIBE_MODEL", "whisper-1")
SUMMARY_MODEL = os.environ.get("OPENAI_SUMMARY_MODEL", "gpt-4o-mini")
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


def _should_retry(exc: Exception) -> bool:
    status = getattr(exc, "status", None) or getattr(exc, "http_status", None)
    status_code = getattr(exc, "status_code", None)
    return any(code == 429 for code in (status, status_code))


def _with_retries(func, *, retries: int = 3, backoff: float = 1.5):
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return func()
        except OpenAIError as exc:  # pragma: no cover - network errors are external
            last_error = exc
            if attempt == retries - 1 or not _should_retry(exc):
                break
            delay = backoff**attempt
            time.sleep(delay)
    assert last_error is not None
    raise RuntimeError(f"OpenAI speech request failed after retries: {last_error}") from last_error


def transcribe_audio(
    file_path: str | Path,
    *,
    translate: bool = False,
    language: str | None = None,
) -> Dict[str, str]:
    """Transcribe (and optionally translate) an audio file."""

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    client = _client()

    def _request():
        with file_path.open("rb") as audio:
            return client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=audio,
                response_format="text",
                language=language,
                translate=translate,
            )

    try:
        result = _with_retries(_request)
    except RuntimeError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Transcription failed: {exc}") from exc

    transcript = result if isinstance(result, str) else getattr(result, "text", "")
    filename_stem = f"transcript-{time.strftime('%Y%m%dT%H%M%S')}"
    output_path = build_artifact_path(WHISPER_DIR, filename_stem, ext="txt")
    output_path.write_text(transcript, encoding="utf-8")

    return {
        "path": str(output_path),
        "text": transcript,
        "translated": translate,
    }


def summarize_text(text: str, *, model: str | None = None) -> Dict[str, str]:
    """Summarize a transcript using the chat model and save the summary."""

    if not text.strip():
        raise ValueError("Cannot summarize empty text")

    model_name = model or SUMMARY_MODEL
    client = _client()

    def _request():
        return client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Produce a concise bullet summary of the provided transcript.",
                },
                {"role": "user", "content": text},
            ],
            temperature=float(os.environ.get("OPENAI_SUMMARY_TEMPERATURE", "0.2")),
            max_tokens=int(os.environ.get("OPENAI_SUMMARY_MAX_TOKENS", "400")),
        )

    try:
        completion = _with_retries(_request)
    except RuntimeError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Summary generation failed: {exc}") from exc

    summary = completion.choices[0].message.content if completion.choices else ""
    filename_stem = f"summary-{time.strftime('%Y%m%dT%H%M%S')}"
    output_path = build_artifact_path(LOG_DIR, filename_stem, ext="md")
    output_path.write_text(summary, encoding="utf-8")

    return {"path": str(output_path), "summary": summary, "model": model_name}


def text_to_speech(text: str, *, voice: str | None = None, model: str | None = None) -> Dict[str, str]:
    """Convert text to speech and save the audio file to disk."""

    if not text.strip():
        raise ValueError("Cannot synthesize speech from empty text")

    voice_name = voice or DEFAULT_VOICE
    model_name = model or TTS_MODEL
    client = _client()

    def _request():
        return client.audio.speech.create(
            model=model_name,
            voice=voice_name,
            input=text,
        )

    try:
        response = _with_retries(_request)
    except RuntimeError as exc:  # pragma: no cover - network errors are external
        raise RuntimeError(f"Text-to-speech failed: {exc}") from exc

    filename_stem = f"tts-{time.strftime('%Y%m%dT%H%M%S')}"
    output_path = build_artifact_path(LOG_DIR, filename_stem, ext="mp3")

    audio_bytes = response.read() if hasattr(response, "read") else response
    if isinstance(audio_bytes, str):  # pragma: no cover - defensive
        audio_bytes = audio_bytes.encode("utf-8")
    output_path.write_bytes(audio_bytes)

    return {
        "path": str(output_path),
        "voice": voice_name,
        "model": model_name,
    }


__all__ = [
    "transcribe_audio",
    "summarize_text",
    "text_to_speech",
    "is_configured",
]
