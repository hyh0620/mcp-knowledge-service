# Salon Example

This example demonstrates how a business application can use MCP Knowledge Service with a domain-specific collection.

## Collection

```text
salon_knowledge
```

## Source Files

Markdown sources live in `knowledge_sources/`. Generated PDFs live in `generated_pdfs/` and are used as ingestion input for the verified example.

## Ingest

```bash
python examples/salon/ingest_salon_example.py
```

Equivalent command:

```bash
python scripts/ingest.py \
  --path examples/salon/generated_pdfs \
  --collection salon_knowledge \
  --force
```

## Query

```bash
python scripts/query.py \
  --query "染发前后有什么注意事项？" \
  --collection salon_knowledge \
  --top-k 4
```

This example is intentionally kept outside the root service defaults.
