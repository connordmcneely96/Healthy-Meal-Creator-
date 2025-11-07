# Unified AI Lab Monorepo

A production-ready monorepo starter that blends a Next.js 14 web app with a local Streamlit tool. The repository is optimised for GitHub Codespaces out of the box and ready for Vercel deployments.

## Quickstart (local machine)

1. **Clone and install dependencies**
   ```bash
   git clone <your-fork-url>
   cd Healthy-Meal-Creator-
   pnpm install
   pnpm -C web install
   python -m venv .venv && source .venv/bin/activate
   pip install -r app/requirements.txt
   ```
2. **Set environment variables**
   - Copy `.env.example` to `.env` (for Streamlit) and `web/.env.local` for the Next.js app.
   - Provide values for `OPENAI_API_KEY` and any `NEXT_PUBLIC_*` variables.
3. **Run the apps**
   - Web: `pnpm dev:web` (or `pnpm --filter ./web dev`) and open <http://localhost:3000>.
   - Streamlit: `pnpm dev:app` or `streamlit run app/Home.py` and open <http://localhost:8501>.

## Quickstart (GitHub Codespaces)

1. Create a Codespace from this repository. The devcontainer installs Node 20, pnpm, Python 3.10+, ffmpeg, and VS Code extensions automatically.
2. On first boot, the `postCreateCommand` runs `pnpm -C web install` and `pip install -r app/requirements.txt`.
3. Start the apps:
   - `pnpm dev:web`
   - `pnpm dev:app`
4. Codespaces auto-forwards ports 3000 (Next.js) and 8501 (Streamlit). Use the “Ports” panel to open previews.

## Deploy to Vercel (Next.js web app)

1. Push this repository to GitHub.
2. In Vercel, create a new project from the repo and set **Root Directory** to `web`.
3. Add the required environment variables (e.g. `OPENAI_API_KEY`, `NEXT_PUBLIC_APP_NAME`) via **Settings → Environment Variables**.
4. Trigger a deployment. Vercel will auto-detect Next.js and use the default build and output settings.

## Environment variables & secrets

- Never commit secrets. Use `.env` locally and Codespaces/Vercel secrets in the cloud.
- For Next.js, create `web/.env.local`. Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser; keep server-only values (like `OPENAI_API_KEY`) without that prefix.
- The Streamlit app reads `.env` at the repository root via `python-dotenv`.

## Scripts reference

Root `package.json` scripts:

| Script | Description |
| --- | --- |
| `pnpm dev:web` | Start the Next.js dev server on port 3000. |
| `pnpm dev:app` | Run the Streamlit tool on port 8501. |
| `pnpm format` | Format the entire repository with Prettier. |
| `pnpm lint` | Run `next lint` for the web workspace. |

`web/package.json` scripts:

| Script | Description |
| --- | --- |
| `pnpm dev` | Run the Next.js development server. |
| `pnpm build` | Create an optimized production build. |
| `pnpm start` | Start Next.js in production mode. |
| `pnpm lint` | Run Next.js linting. |

## Repository structure

```
.
├─ web/               # Next.js 14 App Router app (Vercel target)
├─ app/               # Streamlit local tool
├─ .devcontainer/     # GitHub Codespaces configuration
├─ .github/workflows/ # CI utilities
├─ .env.example
├─ vercel.json
└─ README.md
```

Feel free to extend the components, add API routes, or wire additional tools into this foundation.
