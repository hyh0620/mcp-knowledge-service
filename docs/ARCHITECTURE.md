# Architecture / 系统架构

MCP Knowledge Service is a domain-neutral retrieval service exposed through MCP stdio.

MCP Knowledge Service 是通过 MCP stdio 暴露的通用知识检索服务。

## Ingestion Flow / 知识导入流程

```text
source documents
  -> loader
  -> text extraction
  -> chunking
  -> embeddings
  -> ChromaDB
  -> BM25
  -> collection
```

The ingestion path converts PDF / Markdown source documents into chunks, stores embeddings in ChromaDB, and builds BM25 documents for sparse retrieval.

导入流程把 PDF / Markdown 知识源转换为 chunks，写入 ChromaDB 向量库，并构建 BM25 文档用于关键词检索。

## Query Flow / 查询流程

```text
MCP client
  -> stdio JSON-RPC
  -> query_knowledge_hub
  -> Dense Retrieval
  -> BM25
  -> RRF
  -> citations
```

The service combines Dense Retrieval and BM25 results with RRF, then returns cited results to the MCP client.

服务使用 RRF 融合 Dense Retrieval 与 BM25 结果，并向 MCP Client 返回带 citations 的检索结果。

## MCP Server / MCP 服务

Entry point:

```bash
python -m src.mcp_server.server
```

`python -m src.mcp_server.server` starts an stdio JSON-RPC server, not an interactive CLI.

For normal application use, let the MCP client launch it automatically.

For standalone verification, start it through an MCP client or verification script that sends `initialize`, `tools/list`, and tool calls.

`python -m src.mcp_server.server` 启动的是 stdio JSON-RPC Server，不是可直接交互查询的 CLI。

正常业务运行时，应由 MCP Client 自动拉起该进程。

单独验证时，应通过 MCP Client 或验证脚本发送 `initialize`、`tools/list` 和 tool call，而不是只在终端直接运行该命令。

Tools:

- `query_knowledge_hub`
- `list_collections`
- `get_document_summary`

Stdout is reserved for MCP JSON-RPC protocol messages. Logs must go to stderr.

stdout 只承载 MCP JSON-RPC 协议消息；日志写入 stderr。

## Collection Isolation / Collection 隔离

Collections isolate data between business domains. The service default is `knowledge_hub`, while examples can use explicit collections such as `salon_knowledge`.

collection 是业务知识隔离单位。服务默认 collection 是 `knowledge_hub`，示例可以显式使用 `salon_knowledge`。

Collection names should come from CLI arguments, MCP tool input, environment variables, or config.

collection 名称应来自 CLI 参数、MCP tool 输入、环境变量或配置，不应在核心服务代码中写死具体业务。

## Runtime Data / 运行时数据

Runtime data is written under local storage such as `data/` and `logs/`. These directories must not be committed.

ChromaDB、BM25、SQLite、日志和 trace 等运行时数据不提交到 Git。
