---
name: ingest-knowledge
description: Ingest a source path into a specified collection and report file, chunk, vector, and BM25 counts.
---

# Ingest Knowledge

## Inputs

- Source path.
- Collection name.
- Optional `--dry-run`.

## Pipeline

1. Dry run:
   ```bash
   python scripts/ingest.py --path <SOURCE_PATH> --collection <COLLECTION> --dry-run
   ```
2. Ingest:
   ```bash
   python scripts/ingest.py --path <SOURCE_PATH> --collection <COLLECTION> --force
   ```
3. Verify query:
   ```bash
   python scripts/query.py --query "<QUERY>" --collection <COLLECTION> --top-k 4
   ```
4. Inspect runtime counts from command output and local ChromaDB/BM25 metadata.

## Output

- Files processed.
- Failed files.
- Chunk count.
- Vector count.
- BM25 document count.
- Collection name.

## Rules

- Do not commit `data/`, `logs/`, traces, or generated runtime reports.
