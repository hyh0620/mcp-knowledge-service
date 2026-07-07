# MCP Knowledge Service

Reusable MCP-based knowledge retrieval service for domain-specific document ingestion and cited hybrid retrieval.

可复用的 MCP 知识检索服务，通过 collection 隔离不同业务知识库，提供文档导入、混合检索和来源引用。

## Overview / 项目概述

MCP Knowledge Service is a domain-neutral retrieval server exposed through the Model Context Protocol. It ingests documents into named collections, builds Dense Retrieval and BM25 indexes, fuses results with RRF, and returns cited search results to MCP clients.

该服务不绑定具体业务。`examples/salon/` 只是一个可运行的示例，用于展示业务项目如何通过 collection 接入自己的知识库。

## Core Capabilities / 核心能力

| Capability | English | 中文说明 |
| --- | --- | --- |
| MCP stdio server | Uses the official MCP Python SDK and stdio JSON-RPC transport. | 通过标准 MCP stdio transport 暴露工具，便于被业务系统作为独立进程调用。 |
| Ingestion | Imports PDF / Markdown knowledge sources into a selected collection. | 支持把指定知识源导入到指定 collection，不把业务域写死在服务代码中。 |
| Collection isolation | Collections are selected through CLI arguments, MCP tool input, environment, or config. | 不同业务知识库通过 collection 隔离，例如 `knowledge_hub`、`salon_knowledge`。 |
| Hybrid Retrieval | Combines ChromaDB Dense Retrieval, BM25, and RRF Fusion. | 同时利用向量检索和关键词检索，再通过 RRF 融合排序。 |
| Citations | Returns source metadata for cited answers. | 检索结果带来源信息，方便上层应用展示引用。 |
| OpenAI-compatible provider | Supports Qwen-compatible OpenAI API configuration. | 可通过 OpenAI-compatible 配置接入 Qwen embedding 或其他兼容 Provider。 |

## Architecture / 系统架构

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

## Collection Isolation / Collection 隔离

Collection names isolate domain-specific knowledge retrieval. Examples:

- `knowledge_hub`
- `salon_knowledge`
- `email_knowledge`
- `internal_policy_knowledge`

Collection names must be passed through CLI arguments, MCP tool arguments, environment variables, or config. Service code should not hardcode a business-specific collection.

## Quick Start / 快速启动

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
```

Fill local provider values in `.env` or shell environment before real embedding or provider-backed ingestion. Do not commit `.env` or `config/settings.yaml`.

真实执行 embedding 或 Provider 驱动的 ingestion 前，在本地 `.env` 或 shell 环境中填入私有 Key；不要提交这些配置。

MCP server entry point:

```bash
python -m src.mcp_server.server
```

`python -m src.mcp_server.server` starts an stdio JSON-RPC server, not an interactive CLI.

For normal application use, let the MCP client launch it automatically.

For standalone verification, start it through an MCP client or verification script that sends `initialize`, `tools/list`, and tool calls.

The server uses stdio transport. Stdout is reserved for MCP protocol messages; logs are written to stderr.

`python -m src.mcp_server.server` 启动的是 stdio JSON-RPC Server，不是可直接交互查询的 CLI。

正常业务运行时，应由 MCP Client 自动拉起该进程。

单独验证时，应通过 MCP Client 或验证脚本发送 `initialize`、`tools/list` 和 tool call，而不是只在终端直接运行该命令。

## Ingestion / 知识导入

Ingest documents into a selected collection:

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

Real ingestion requires provider configuration for embeddings and writable runtime storage. Do not commit runtime ChromaDB, BM25, SQLite, logs, traces, or local reports.

## MCP Tools / MCP 工具

Expected tools from `tools/list`:

- `query_knowledge_hub`
- `list_collections`
- `get_document_summary`

MCP tool input for `query_knowledge_hub`:

```json
{
  "query": "What is this collection about?",
  "top_k": 4,
  "collection": "knowledge_hub"
}
```

CLI query:

```bash
python scripts/query.py \
  --query "What is this collection about?" \
  --collection knowledge_hub \
  --top-k 4
```

## Verified Public Scope / 已验证公开范围

- MCP initialize
- `tools/list`
- `query_knowledge_hub`
- citations
- salon example ingestion: 7 PDFs, 24 chunks, 24 vectors, 24 BM25 documents
- `smoke_test_collection` proves collection is not hardcoded
- runtime data is intentionally excluded from Git

The salon example verification is an integration check, not a general retrieval-quality benchmark.

## Example Integration / 示例集成

The `examples/salon/` directory contains a complete example used by AI Hair Salon Agent:

- 7 source Markdown files
- generated PDFs
- ingestion instructions
- example collection: `salon_knowledge`

It is an integration example, not the default domain of this repository.

## Related Repository / 关联项目

AI Hair Salon Agent: <https://github.com/hyh0620/ai-hair-salon-agent>

AI Hair Salon Agent is a reference consumer that calls this service through an MCP client with `collection=salon_knowledge`.

AI Hair Salon Agent 是该服务的参考消费者，通过 MCP Client 调用 `salon_knowledge` collection。

## Verification / 验证方式

Static dependency check:

```bash
.venv/bin/python -m pip check
```

Unit and integration tests:

```bash
pytest
```

Real MCP verification:

```text
initialize -> tools/list -> query_knowledge_hub
```

Real ingestion verification:

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection <COLLECTION_NAME> \
  --force
```

Some real ingestion and provider tests require local provider configuration, API credentials, and runtime storage. Keep those local files out of Git.

## Known Limits / 当前限制

| Limit | 中文说明 |
| --- | --- |
| No authentication or authorization layer is claimed. | 当前公开范围不声明认证、授权或企业级租户安全控制。 |
| No Dashboard, Rerank, Ragas, multimodal, or Vision claim. | 未验证高级模块不作为公开能力。 |
| Runtime ChromaDB, BM25, SQLite, logs, and traces are not committed. | 运行时数据不进入 Git，复现时需本地重新导入。 |
| The salon example is not the default business domain. | 根服务是通用知识检索服务，理发店只是示例集成。 |

## Documentation / 文档

- [Architecture / 系统架构](docs/ARCHITECTURE.md)
- [Ingestion / 知识导入](docs/INGESTION.md)
- [Integration / 接入指南](docs/INTEGRATION.md)
- [Evaluation / 检索评估](docs/EVALUATION.md)

## Skills / 项目工作流

Operational skills are under `.github/skills/`:

- `setup-environment`
- `ingest-knowledge`
- `verify-mcp-server`
- `evaluate-retrieval`
- `package-clean`

They describe repeatable operational workflows and do not contain credentials.

## Security / 安全说明

Do not commit `.env`, API keys, `config/settings.yaml`, local runtime databases, ChromaDB files, BM25 indexes, logs, trace files, or raw local evaluation dumps.
