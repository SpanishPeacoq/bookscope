# 0002. Adopt Gradio Space MVP

## Status

Accepted

## Context

The Build Small hackathon requires a runnable Hugging Face Space. Bookscope needs to move quickly from idea to demo, and the highest-risk failure mode is building separate pieces that do not connect before the deadline.

## Decision

Use a small Gradio app as the primary product surface and Hugging Face Space entrypoint. The first loop is:

```text
shelf image -> vision extraction -> editable table -> metadata enrichment
```

The vision provider remains configurable through environment variables so the app can start in demo mode, then call a hosted MiniCPM-V model once the exact provider path is confirmed.

## Consequences

- The app is immediately deployable as a Space.
- Image and later frame-sampled video flows can share the same extraction and enrichment pipeline.
- The current app does not persist raw shelf images, which keeps the privacy story simple for the hackathon demo.
- Provider-specific MiniCPM-V behavior is isolated behind a small adapter instead of spread through the UI.
