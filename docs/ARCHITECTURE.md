# Architecture / 系统架构

MCP Knowledge Service is an MCP Server for domain-specific document ingestion and cited Hybrid Retrieval.

MCP Knowledge Service 是用于领域文档导入和带引用混合检索的 MCP Server。

![Architecture](../architecture.svg)

## Knowledge Preparation / 知识准备

Knowledge preparation is the offline path. It converts source documents into collection-scoped retrieval data.

知识准备是离线路径，把源文档转换为指定 collection 下的检索数据。

Source documents can be Markdown or PDF. `salon_knowledge` is only an example collection used by `examples/salon/`, not the default service domain.

知识源可以是 Markdown 或 PDF。`salon_knowledge` 只是 `examples/salon/` 使用的示例 collection，不是服务默认业务领域。

## Ingestion Pipeline / 导入流程

```text
source documents
  -> loader
  -> text extraction
  -> normalization
  -> chunking
```

The pipeline prepares clean text chunks before retrieval indexes are built.

导入流程先把文档转换为可检索的文本 chunks。

## Retrieval Storage / 检索存储

Chunks are stored in two retrieval paths:

- embeddings -> ChromaDB Vector Store
- chunk terms -> BM25 Index

chunks 同时进入向量检索和 BM25 关键词检索路径。

Runtime ChromaDB data, BM25 indexes, SQLite files, logs, and traces stay local and are not committed to Git.

ChromaDB、BM25 index、SQLite、日志和 trace 等运行时数据保留在本地，不提交到 Git。

## MCP Serving Layer / MCP 服务层

The online serving path is an MCP stdio JSON-RPC server process.

在线查询路径是 MCP stdio JSON-RPC server 进程。

```bash
python -m src.mcp_server.server
```

`python -m src.mcp_server.server` starts an stdio JSON-RPC server, not an interactive CLI. For normal application use, let the MCP client launch it automatically.

`python -m src.mcp_server.server` 启动的是 stdio JSON-RPC Server，不是可直接交互查询的 CLI；正常业务运行时应由 MCP Client 自动拉起。

The service exposes knowledge retrieval tools:

- `query_knowledge_hub`
- `list_collections`
- `get_document_summary`

该服务暴露的是知识检索 tools。

`stdout` is reserved for MCP JSON-RPC protocol messages. Logs are written to `stderr`.

`stdout` 只承载 MCP JSON-RPC 协议消息；日志写入 `stderr`。

## Query Execution / 查询执行

```text
Consumer Application / MCP Client
  -> stdio JSON-RPC
  -> MCP Knowledge Service (MCP Server)
  -> query_knowledge_hub
  -> Dense Retrieval + BM25 Retrieval
  -> RRF Fusion
```

`query_knowledge_hub` runs Dense Retrieval and BM25 Retrieval, then fuses ranked results with RRF.

`query_knowledge_hub` 执行 Dense Retrieval 与 BM25 Retrieval，并通过 RRF 融合排序结果。

## Collection Isolation / Collection 隔离

Collections isolate domain-specific knowledge. Examples:

- `knowledge_hub`
- `salon_knowledge` (example)

collection 是业务知识隔离单位。`salon_knowledge` 是示例 collection，不是默认业务域。

Collection names should come from CLI arguments, MCP tool input, environment variables, or config.

collection 名称应来自 CLI 参数、MCP tool 输入、环境变量或配置。

## Output and Citations / 输出与引用

The serving layer returns Retrieved Answer with Citations.

服务层返回 Retrieved Answer with Citations，即检索结果和来源引用。

Callers should preserve citations and display them when useful to users.

调用方应保留 citations，并在适合的用户界面中展示来源。

## Runtime Boundaries / 运行时边界

This public service does not claim authentication, authorization, tenant isolation, production security controls, or production deployment.

当前公开范围不声明认证、授权、租户隔离、生产级安全控制或生产部署。

It does not claim Rerank, Ragas, Vision, multimodal processing, Graph RAG, or Memory.

当前公开范围不声明 Rerank、Ragas、Vision、多模态、Graph RAG 或 Memory。
