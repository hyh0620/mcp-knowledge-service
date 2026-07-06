---
name: verify-mcp-server
description: Start the real stdio MCP server, initialize it, list tools, and query a configured collection.
---

# Verify MCP Server

## Pipeline

1. Ensure `config/settings.yaml` and provider environment variables are configured locally.
2. Start through an MCP client using:
   ```bash
   python -m src.mcp_server.server
   ```
3. Call `initialize`.
4. Call `tools/list`.
5. Confirm tools:
   - `query_knowledge_hub`
   - `list_collections`
   - `get_document_summary`
6. Call:
   ```json
   {
     "query": "What is this collection about?",
     "top_k": 4,
     "collection": "knowledge_hub"
   }
   ```

## Output

- Initialization status.
- Tool names.
- Query status.
- Citation count and source names.

## Failure Handling

- If stdout contains logs, fix logging before continuing.
- If tools are missing, inspect MCP server registration.
- If citations are empty, verify collection ingestion.
