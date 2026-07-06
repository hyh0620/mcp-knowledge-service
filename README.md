# MCP Knowledge Service

MCP Knowledge Service is a reusable knowledge retrieval server exposed through the Model Context Protocol. It provides ingestion, collection-based isolation, Hybrid Retrieval, and cited results for business applications that need private knowledge access.

The service is domain-neutral. Salon knowledge is included only as an example under `examples/salon/`.

## Core Capabilities

- MCP stdio server using the official MCP Python SDK.
- Tools:
  - `query_knowledge_hub`
  - `list_collections`
  - `get_document_summary`
- Ingestion pipeline for source documents.
- Dense Retrieval with ChromaDB.
- BM25 sparse retrieval.
- RRF Fusion.
- Source citations.
- Collection-based isolation for multiple business domains.
- OpenAI-compatible provider configuration, including Qwen compatible mode.

## Architecture

```text
Source documents
  -> ingestion pipeline
  -> chunks
  -> embeddings + ChromaDB
  -> BM25 index
  -> collection

MCP client
  -> stdio JSON-RPC
  -> query_knowledge_hub
  -> Dense + BM25 + RRF
  -> cited results
```

## Collection Isolation

Collection names isolate business knowledge. Examples:

- `knowledge_hub`
- `salon_knowledge`
- `email_knowledge`
- `internal_policy_knowledge`

Collection names must be passed through CLI arguments, MCP tool arguments, environment variables, or config. Service code should not hardcode a business-specific collection.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
```

Fill local provider values in `.env`. Do not commit `.env` or `config/settings.yaml`.

## Ingest Documents

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection knowledge_hub \
  --force
```

Dry run:

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection knowledge_hub \
  --dry-run
```

## Start MCP Server

```bash
python -m src.mcp_server.server
```

The server uses stdio transport. Stdout is reserved for MCP protocol messages; logs are written to stderr.

## Verify Tools

Use an MCP client to initialize the server and call `tools/list`. Expected tools:

- `query_knowledge_hub`
- `list_collections`
- `get_document_summary`

## Query

CLI query:

```bash
python scripts/query.py \
  --query "What is this collection about?" \
  --collection knowledge_hub \
  --top-k 4
```

MCP tool input:

```json
{
  "query": "What is this collection about?",
  "top_k": 4,
  "collection": "knowledge_hub"
}
```

## Salon Example

The `examples/salon/` directory contains a complete example used by AI Hair Salon Agent:

- 7 source Markdown files
- generated PDFs
- ingestion instructions
- example collection: `salon_knowledge`

It is an integration example, not the default domain of this repository.

## Tests

```bash
.venv/bin/python -m pip check
```

Additional unit/integration tests may require local provider credentials or generated runtime data. Keep runtime data out of git.

## Known Limits

- Rerank is disabled in the public example configuration.
- Ragas evaluation is not claimed as part of the verified public release.
- Multimodal workflows are not claimed as verified public functionality.
- Runtime ChromaDB, BM25, SQLite, logs, and traces are not committed.

## Skills

Operational skills are under `.github/skills/`:

- `setup-environment`
- `ingest-knowledge`
- `verify-mcp-server`
- `evaluate-retrieval`
- `package-clean`

They describe repeatable operational workflows and do not contain credentials.
