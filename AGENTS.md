# AGENTS.md

This file is the repo-local operating manual for coding agents. It extends the user's global Codex instructions.

## Project Mission

Bookscope is early-stage. Until the product and stack are chosen, keep the repository organized around clear documentation, safe collaboration, and small verified changes.

## Non-Negotiables

- Preserve user changes. Do not revert or overwrite work you did not make unless explicitly instructed.
- Keep changes scoped to the requested task.
- Prefer simple, durable designs over clever abstractions.
- Do not change architecture, business rules, data contracts, or security posture without updating or adding an ADR.
- Never commit secrets, credentials, private keys, tokens, or live `.env` values.

## First Steps

Before substantial edits:

- Check `git status` and current branch.
- Read `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/architecture.md`, and relevant ADRs.
- Identify the smallest safe change that satisfies the request.
- If multiple agents are working, state which files or modules you intend to own.

## Commands

```bash
pip install -r requirements.txt

python app.py

python -m compileall app.py bookscope.py

# no lint command is configured yet
```

## Multi-Agent Coordination

- Avoid parallel edits to the same file when possible.
- If overlap is unavoidable, coordinate through small commits or explicit patches.
- Do not silently rewrite another agent's work.
- Leave unresolved assumptions in the task thread or a dedicated note.
- Keep documentation updates close to behavior, setup, architecture, or security changes.

## Testing Expectations

- Add or update tests for behavior changes, bug fixes, migrations, and risky refactors.
- Run relevant tests before claiming completion.
- If tests cannot be run, explain why and describe the risk.
- Prefer small regression tests that prove the changed behavior directly.

## Security Expectations

- Treat authentication, authorization, dependency changes, command execution, database queries, file upload, and external callbacks as security-sensitive.
- Validate inputs at trust boundaries.
- Use least-privilege defaults.
- Redact secrets in logs and documentation.

## Definition Of Done

- The change is implemented and scoped.
- Relevant tests or checks have been run, or blockers are documented.
- Security-sensitive surfaces have been considered.
- Relevant docs and ADRs are updated.
- `git status` has been reviewed.
- Finished work is committed and pushed when credentials and user intent allow.
