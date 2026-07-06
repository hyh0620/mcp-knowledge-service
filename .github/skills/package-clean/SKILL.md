---
name: package-clean
description: Prepare a public package by checking ignored files, runtime data, secrets, and old project content.
---

# Package Clean

## Pipeline

1. Dry-run file scan:
   ```bash
   find . -maxdepth 3 -type d \( -name .venv -o -name data -o -name logs -o -name __pycache__ -o -name .pytest_cache \)
   ```
2. Confirm `.gitignore` excludes:
   - `.env`
   - `config/settings.yaml`
   - `.venv/`
   - `data/`
   - `logs/`
   - caches
3. Search for old or sensitive content:
   ```bash
   git grep -n -I -E "(api[_-]?key|secret|token)[[:space:]]*[:=][[:space:]]*[^< ]{12,}|old-project-name|legacy-author"
   ```
4. Remove runtime directories only after confirming they are generated artifacts.
5. Keep public examples under `examples/`.

## Output

- Files excluded.
- Findings that require manual review.
- Final clean status.

## Rules

- Do not delete source documents in `examples/salon`.
- Do not print or copy secrets.
