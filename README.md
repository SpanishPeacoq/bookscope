---
title: Bookscope
sdk: gradio
app_file: app.py
pinned: false
tags:
  - hackathon
  - backyard-ai
  - vision
  - ocr
  - minicpm-v
  - codex
---

# Bookscope

Bookscope turns messy shelf photos into a searchable used-book inventory. It is built for the used bookstore problem: rotated spines, partial titles, mixed categories, and shelves that are valuable but hard to browse.

## Hackathon MVP

The first working loop is intentionally small:

1. Upload or capture a shelf photo.
2. Extract visible book candidates into an editable table.
3. Enrich the rows with public book metadata from Open Library.
4. Keep structured inventory rows, not raw shelf photos, by default.

The vision model is provider-swappable. The app runs in demo mode without secrets, then calls a configured Hugging Face-hosted MiniCPM-V model when `HF_TOKEN` and `BOOKSCOPE_HF_MODEL` are set.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Copy `.env.example` to `.env` for local development and set real values locally. Never commit secrets.

## Configuration

| Variable | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face token for the selected hosted model/provider. |
| `BOOKSCOPE_HF_MODEL` | Model or endpoint identifier used by `huggingface_hub.InferenceClient`. |
| `BOOKSCOPE_HF_PROVIDER` | Optional Hugging Face inference provider name. |
| `BOOKSCOPE_DEMO_MODE` | Set to `false` to force live model calls. Defaults to demo mode when model config is missing. |

## Privacy Boundary

Bookscope is designed to process shelf images transiently and save structured book rows. Raw images are not persisted by the current app. A future scan-session feature may optionally save thumbnails only when the user asks for audit/debug history.

## Project Structure

```text
.
|-- app.py
|-- bookscope.py
|-- requirements.txt
|-- README.md
|-- AGENTS.md
|-- CONTRIBUTING.md
|-- SECURITY.md
|-- docs/
|   |-- architecture.md
|   `-- adr/
`-- .github/
```

## Built With Codex

The initial Gradio MVP was built with OpenAI Codex as an implementation collaborator. Commits for hackathon work should keep clear messages and include a Codex co-author trailer when appropriate.

## Status

Current status: runnable Gradio MVP with demo scan rows, provider hook for Hugging Face vision inference, and Open Library enrichment.
