# Architecture

This document describes the current system shape. Keep it factual and short enough that future contributors will actually read it.

## Purpose

Bookscope is early-stage. The product purpose, primary users, and key workflows still need to be defined.

## Current System

The repository currently contains only the project baseline: documentation, contribution rules, security expectations, and GitHub collaboration defaults.

## Components

| Component | Responsibility | Notes |
| --- | --- | --- |
| Documentation baseline | Records setup, architecture, contribution, and security expectations | Present |
| Application code | Product implementation | Not selected yet |
| Tests | Automated verification | Not selected yet |

## Data Flow

No runtime data flow exists yet.

```text
TODO: define once application behavior exists
```

## Boundaries

- External services: none defined yet.
- Databases: none defined yet.
- File system: repository files only.
- Network calls: none defined yet.
- User input: none defined yet.

## Runtime And Deployment

No runtime, deployment target, or hosting model has been selected yet.

## Important Decisions

Record durable decisions in `docs/adr/`. Link the most relevant ADRs here.

- `docs/adr/0001-record-project-baseline.md`

## Known Risks

- The project stack and product requirements are not defined yet.
- Commands in `README.md` and `AGENTS.md` are placeholders until tooling is chosen.

## Update Rule

Update this file when the system shape, major boundaries, or deployment model changes.
