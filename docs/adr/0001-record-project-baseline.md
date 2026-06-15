# 0001 Record Project Baseline

Status: Accepted

Date: 2026-06-14

## Context

The project needs a small, durable documentation and collaboration baseline so humans and coding agents can work safely without repeating setup instructions in every task.

## Decision

Use the following baseline files:

- `README.md` for project purpose, setup, and common commands.
- `AGENTS.md` for coding-agent operating rules.
- `CONTRIBUTING.md` for contribution and multi-agent workflow.
- `SECURITY.md` for security expectations.
- `docs/architecture.md` for the current system map.
- `docs/adr/` for important decisions.
- `.env.example` and `.gitignore` for local configuration hygiene.
- `.github/` for collaboration templates and automation when hosted on GitHub.

## Consequences

The project starts with a little more structure, but the structure is intentionally small and useful. Contributors should keep these files accurate and avoid adding process documents that do not answer recurring questions or preserve important decisions.
