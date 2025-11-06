# Healthy Meal Creator

A production-ready Streamlit application showcasing three OpenAI-powered tools:
meal planning, image generation, and speech utilities. Built to run locally or
as a free [Hugging Face Space](https://huggingface.co/spaces).

## Features

- **Diagnostics home** with environment health checks
- **Meal Plan Studio** for generating structured nutrition plans
- **Image Studio** for DALL·E powered visuals
- **Speech Lab** for Whisper transcription and text-to-speech
- **Gallery** to browse generated artifacts
- **Settings** page to manage API keys without persisting secrets

## Quick start

### 1. Clone and install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy the sample environment file and fill in your OpenAI key:

```bash
cp .env.sample .env
```

Alternatively, set secrets directly in Hugging Face Space settings.

### 3. Run locally

```bash
streamlit run app/Home.py
```

### 4. Deploy to Hugging Face Spaces

1. Create a new **Streamlit** Space.
2. Upload this repository's files.
3. In the Space settings, add `OPENAI_API_KEY` as a secret.
4. Trigger a rebuild. The Space will launch automatically.

## Data storage

All generated artifacts are stored under `data/`:

- `data/meal_plan` – meal plan JSON logs
- `data/dalle` – generated image files
- `data/whisper` – Whisper transcripts
- `data/logs` – speech synthesis outputs and miscellaneous logs

These directories are created automatically at runtime.

## Testing

Run the automated tests to validate project structure:

```bash
pytest
```

## Licensing

This project is licensed under the terms of the MIT License. See
[LICENSE](LICENSE) for details.
