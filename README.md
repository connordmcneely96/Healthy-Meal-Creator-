# Healthy Meal Creator

A production-ready Streamlit application that demonstrates three OpenAI-powered
workflows: meal planning, image generation, and speech utilities. The project is
optimized for local execution and free hosting on [Hugging Face Spaces](https://huggingface.co/spaces).

## Features

- **Diagnostics home** with environment health checks
- **Meal Plan Studio** for generating structured nutrition plans
- **Image Studio** for GPT-image creation and editing workflows
- **Speech Lab** for Whisper transcription, summarization, and TTS playback
- **Gallery** to browse generated artifacts saved under `data/`
- **Settings** page to manage API keys without persisting secrets

## Getting started locally

1. **Clone and install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**

   ```bash
   cp .env.sample .env
   # edit .env to include your OpenAI API key
   ```

3. **Run Streamlit**

   ```bash
   streamlit run app/Home.py
   ```

## Deploying to Hugging Face Spaces

1. Create a new Space and choose the **Streamlit** SDK.
2. Connect the Space to this GitHub repository or upload the project files.
3. In the Space **Settings → Secrets** tab, add `OPENAI_API_KEY` with your key.
4. In **Runtime → App**, set the Run command to:

   ```bash
   streamlit run app/Home.py
   ```

5. Restart or rebuild the Space. Once the build completes, the app will launch automatically.

## Data storage

Generated artifacts are organized under `data/`:

- `data/meal_plan` – structured meal plans and Markdown exports
- `data/dalle` – generated image files
- `data/whisper` – transcripts, translations, and summaries
- `data/logs` – application log files and audio synthesis outputs

Directories are created on demand; no manual setup is required.

## Testing

Run the automated tests to validate path helpers and basic imports:

```bash
pytest
```

## Screenshots

Screenshots can be placed under `docs/screenshots/` once captured:

- ![Home page](docs/screenshots/home.png)
- ![Meal plan workflow](docs/screenshots/meal-plan.png)
- ![Image studio](docs/screenshots/image-studio.png)

## License

This project is licensed under the terms of the MIT License. See
[LICENSE](LICENSE) for full text.
