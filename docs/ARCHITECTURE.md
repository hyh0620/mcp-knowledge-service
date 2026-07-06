# Architecture

MCP Knowledge Service is a domain-neutral retrieval service.

## Ingestion Flow

```text
Source file or directory
  -> loader
  -> text extraction
  -> chunking
  -> optional rule-based refinement
  -> embedding
  -> ChromaDB vector store
  -> BM25 index
  -> collection
```

## Query Flow

```text
MCP client
  -> stdio JSON-RPC
  -> query_knowledge_hub
  -> dense retriever
  -> sparse retriever
  -> RRF fusion
  -> response builder
  -> citations
```

## MCP Server

Entry point:

```bash
python -m src.mcp_server.server
```

Tools:

- `query_knowledge_hub`
- `list_collections`
- `get_document_summary`

Stdout is reserved for MCP protocol messages. Logs must go to stderr.

## Collection Isolation

Collections isolate data between business domains. The service default is `knowledge_hub`, while examples can use explicit collections such as `salon_knowledge`.

## Runtime Data

Runtime data is written under `data/` and `logs/` by default. These directories must not be committed.
