---
name: setup-environment
description: Prepare MCP Knowledge Service for local ingestion and MCP server verification.
---

# Setup Environment

## Pipeline

1. Check Python:
   ```bash
   python3.11 --version
   ```
2. Create or reuse `.venv`:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
3. Install:
   ```bash
   pip install -e '.[dev]'
   ```
4. Create local config:
   ```bash
   test -f .env || cp .env.example .env
   test -f config/settings.yaml || cp config/settings.example.yaml config/settings.yaml
   ```
5. Run:
   ```bash
   .venv/bin/python -m pip check
   ```

## Output

- Local `.venv`.
- Ignored local `.env`.
- Ignored local `config/settings.yaml`.

## Failure Handling

- Do not print API keys.
- If provider credentials are missing, stop before ingestion or real query verification.
