---
title: Bookscope
sdk: gradio
app_file: app.py
pinned: false
tags:
  - hackathon
  - backyard-ai
  - best-demo
  - best-agent
  - vision
  - ocr
  - minicpm-v
  - codex
---

# Bookscope

Bookscope turns messy shelf photos into a searchable used-book inventory. It is built for the used bookstore problem: rotated spines, partial titles, mixed categories, and shelves that are valuable but hard to browse.

## Submission Links

- App: https://huggingface.co/spaces/build-small-hackathon/bookscope
- Demo video: TODO: add public demo video URL before the deadline
- Social post: TODO: add public social post URL before the deadline
- GitHub PR with Codex-attributed commits: https://github.com/SpanishPeacoq/bookscope/pull/1
- Team: `SpanishPeacoq`

## Hackathon MVP

The first working loop is intentionally small:

1. Upload or capture a shelf photo.
2. Extract visible book candidates into an editable table.
3. Enrich the rows with public book metadata from Open Library.
4. Correct uncertain rows as a human second pass.
5. Keep structured inventory rows, not raw shelf photos, by default.

The vision model is provider-swappable. In deployed mode, Bookscope defaults to the public `openbmb/MiniCPM-V-4.6-Demo` Space. For offline/local UI work, set `BOOKSCOPE_DEMO_MODE=true` to use built-in sample rows.

## Why This Exists

Used bookstores often contain valuable inventory that is hard to search because the shelves are physically chaotic: spines face different directions, categories are mixed, books are stacked horizontally, and titles are partially hidden. Bookscope treats scanning as an incremental workflow rather than a perfect one-shot OCR problem.

The first pass gives a fast machine read of the shelf. The second pass lets a person correct uncertain rows. Over time, repeated scans can converge into a more reliable shelf inventory without asking the store owner to reorganize the shelves first.

## How It Works

- MiniCPM-V 4.6 reads the uploaded shelf image and returns candidate title/author rows.
- Bookscope normalizes the model response into an editable Gradio table.
- The enrichment step searches Open Library by title and author.
- When available, it adds ISBN, first publish year, publisher, subjects, and an Open Library link.
- If a match is uncertain or missing, the row remains editable instead of pretending the inventory is solved.

## Prize Targets

- Backyard AI: practical daily-life tool for physical shelf inventory.
- Best MiniCPM Build: MiniCPM-V 4.6 is the core vision model.
- Best Use of Codex: the GitHub PR contains Codex co-authored commits.
- Best Agent: the app combines vision extraction, structured row normalization, metadata lookup, and human correction.
- Best Demo: the value is clearest in a before/after shelf scan.

All models used by Bookscope are under the 32B parameter limit. MiniCPM-V 4.6 is listed by the Build Small field guide as an image/OCR model around 1.3B parameters.

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
| `BOOKSCOPE_GRADIO_SPACE` | Optional Hugging Face Space name when the model is exposed through a Gradio demo. Defaults to `openbmb/MiniCPM-V-4.6-Demo`. |
| `BOOKSCOPE_GRADIO_API_NAME` | Gradio API endpoint name, usually `/predict` until inspected. |
| `BOOKSCOPE_GRADIO_INPUT_ORDER` | Space call shape: `minicpm_v46`, `image_prompt`, `prompt_image`, or `image`. |
| `BOOKSCOPE_DEMO_MODE` | Set to `true` for offline sample rows. Leave unset or set to `false` for live MiniCPM-V scans. |

## Privacy Boundary

Bookscope is designed to process shelf images transiently and save structured book rows. Raw images are not persisted by the current app.

Current image handling:

- Gradio receives the uploaded image for the current browser session.
- Bookscope converts it to an in-memory PIL image for scanning.
- Bookscope downsizes very large images before model calls to keep inference responsive.
- When calling the MiniCPM-V Gradio Space, Bookscope writes a temporary JPEG only long enough to send the request, then deletes that temporary file.
- Live MiniCPM-V mode sends the shelf image to the external `openbmb/MiniCPM-V-4.6-Demo` Space on Hugging Face. Bookscope controls its own temporary files, but it cannot control retention or logging inside that upstream public Space.
- The repo ignores local image and video files by default so test shelf photos do not enter Git.
- A future scan-session feature may optionally save thumbnails only when the user asks for audit/debug history.

For sensitive/private shelves, run Bookscope against a model endpoint you control instead of the public demo Space.

## Known Limits

- Wide shelf photos still produce mistakes, especially on tiny, blurry, or partially hidden spines.
- Cropping to one shelf band usually improves recognition.
- Open Library matches are useful but not authoritative; older editions and obscure used books may need manual correction.
- The current app does not persist scan sessions. It focuses on the fast demo loop: image in, candidate rows out, metadata enrichment next.

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

Current status: reviewed Gradio MVP with live MiniCPM-V 4.6 scanning, Open Library enrichment, image-handling documentation, and regression tests for the main failure paths.
