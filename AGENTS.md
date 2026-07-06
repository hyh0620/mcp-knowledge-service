# AGENTS.md

- Python version: 3.11.
- Install: `python3.11 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'`.
- Local config: copy `config/settings.example.yaml` to ignored `config/settings.yaml`.
- MCP server command: `python -m src.mcp_server.server`.
- MCP stdio rule: stdout is reserved for JSON-RPC protocol messages; logs must go to stderr.
- Collection names must come from tool arguments, CLI arguments, environment variables, or config. Do not hardcode `salon_knowledge` in service code.
- Default public collection is `knowledge_hub`; salon data is only an example under `examples/salon`.
- Ingest: `python scripts/ingest.py --path <SOURCE_PATH> --collection <COLLECTION> --force`.
- Query: `python scripts/query.py --query "<QUESTION>" --collection <COLLECTION>`.
- Do not commit `.env`, API keys, `config/settings.yaml`, ChromaDB data, BM25 indexes, SQLite runtime data, logs, traces, or cache files.
- After changing MCP tools or response format, verify initialize, tools/list, `query_knowledge_hub`, citations, and collection isolation.
