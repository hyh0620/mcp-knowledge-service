# Ingestion

The ingestion pipeline converts source documents into retrievable collection data.

## Command

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection <COLLECTION_NAME> \
  --force
```

Dry run:

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection <COLLECTION_NAME> \
  --dry-run
```

## Outputs

The pipeline reports:

- processed files
- failed files
- generated chunks
- stored vectors
- BM25 indexed documents
- image count, if image extraction is enabled

## Collection Names

Pass collection names explicitly. Do not rely on a business-specific default.

## Example

```bash
python scripts/ingest.py \
  --path examples/salon/generated_pdfs \
  --collection salon_knowledge \
  --force
```

Runtime output under `data/` is local and should not be committed.
