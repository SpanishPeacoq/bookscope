# Architecture

This document describes the current system shape. Keep it factual and short enough that future contributors will actually read it.

## Purpose

Bookscope turns messy shelf photos into a searchable used-book inventory. The hackathon MVP focuses on a fast end-to-end loop for used bookstores and home shelf scans: image in, candidate book rows out, public metadata enrichment after review.

## Current System

The repository contains a Gradio application intended for deployment as a Hugging Face Space. The current runtime supports demo-mode scan rows, a Hugging Face vision-model provider hook, and Open Library metadata enrichment.

## Components

| Component | Responsibility | Notes |
| --- | --- | --- |
| `app.py` | Gradio UI and event wiring | Hugging Face Space entrypoint |
| `bookscope.py` | Scan normalization, model-provider call, JSON parsing, metadata enrichment | Keeps UI thin and provider-swappable |
| Hugging Face vision provider | Extracts visible book spines from images | Defaults to `openbmb/MiniCPM-V-4.6-Demo`; set `BOOKSCOPE_DEMO_MODE=true` for offline sample rows |
| Open Library | Enriches candidate rows with ISBN, author, year, publisher, subjects, and links | Public HTTP lookup |
| Documentation baseline | Records setup, architecture, contribution, and security expectations | Present |
| Tests | Automated verification | Not added yet |

## Data Flow

```text
Shelf image
  -> Gradio image input
  -> Hugging Face vision provider or demo records
  -> normalized editable scan table
  -> Open Library search enrichment
  -> enriched inventory table
```

## Boundaries

- External services: optional Hugging Face inference provider and Open Library search API.
- Databases: none defined yet.
- File system: repository files only; uploaded images are not persisted by the app. Temporary JPEGs are created for external Space calls and deleted after each request.
- Network calls: vision inference and metadata enrichment.
- User input: shelf images and editable table rows in the Gradio session.

## Runtime And Deployment

Runtime is Python with Gradio. Deployment target is a Hugging Face Space with `app.py` as the entrypoint.

## Important Decisions

Record durable decisions in `docs/adr/`. Link the most relevant ADRs here.

- `docs/adr/0001-record-project-baseline.md`
- `docs/adr/0002-adopt-gradio-space-mvp.md`

## Known Risks

- Exact hosted MiniCPM-V endpoint/provider configuration still needs verification.
- Video support is not implemented yet; the near-term path is frame sampling that reuses the image pipeline.
- Open Library enrichment depends on public search quality and network availability.

## Update Rule

Update this file when the system shape, major boundaries, or deployment model changes.
