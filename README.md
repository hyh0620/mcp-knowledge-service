# MCP Knowledge Service

## 可复用的 MCP 知识检索服务

这是一个独立的 MCP Server，通过 stdio / JSON-RPC 向 Agent 或业务应用提供知识检索 tools。服务将向量检索（Dense Retrieval）与 BM25 关键词检索结合，再使用倒数排名融合（Reciprocal Rank Fusion, RRF）统一排序，并返回可追溯的来源引用（Citations）。

当前仓库以 salon 作为示例集成，但核心服务通过 collection 选择知识集合，不写死为理发店场景。当前 CLI 直接摄取 PDF；示例中的 Markdown 用作可维护知识源，生成 PDF 后进入 ingestion pipeline。

## 项目简介

MCP Knowledge Service 将文档导入、索引构建和在线查询封装成独立进程。Consumer Application 通过官方 MCP Client 执行 `initialize`、`tools/list` 和 tool call，无需在业务仓库中维护第二套检索实现。

服务负责返回检索上下文和 Citations，不负责上层业务的价格、库存、排班、交易或预约裁决，也不将检索结果包装成完整的业务 LLM 决策。

## 设计目标

- 使用模型上下文协议（MCP）解耦 Agent 与知识检索服务。
- 使用命名 collection 隔离不同领域的索引与查询范围。
- 组合 Dense Retrieval 与 BM25，兼顾语义召回和关键词匹配。
- 使用 RRF 融合异构排名，不依赖原始分数尺度一致。
- 通过 Citations 保留 `source`、文档和 chunk 等来源信息。
- 将协议输出与运行日志分离：`stdout` 仅承载 MCP 消息，日志写入 `stderr`。

## 核心能力

| 能力 | 当前实现 |
| --- | --- |
| MCP Server | Official MCP Python SDK、stdio transport、JSON-RPC、`tools/list` 与 `tools/call`。 |
| 文档导入（Ingestion） | 当前 CLI 直接发现并处理 PDF，执行完整性检查、解析、文本切分（Chunking）、Embedding 和索引写入。 |
| 混合检索（Hybrid Retrieval） | ChromaDB Dense Retrieval + BM25 + RRF。 |
| 来源引用（Citations） | `query_knowledge_hub` 返回检索文本及 References 数据，供调用方展示来源。 |
| Collection | collection 通过 CLI、MCP tool 参数或配置指定；默认名称为 `knowledge_hub`。 |
| Provider | OpenAI-compatible 配置，可接入 Qwen embedding Provider。 |

## 系统架构

![系统架构](./architecture.svg)

- Ingestion：Markdown 可作为维护源；当前实际输入为 PDF，导入后生成 collection 对应的 ChromaDB vectors 与 BM25 documents。
- MCP Serving：Consumer Application 使用 MCP Client 通过 stdio 调用 MCP Server 暴露的 tools。
- Query：`query_knowledge_hub` 执行 Dense Retrieval、BM25 和 RRF，返回检索结果与 Citations。

## 数据导入流程

```text
PDF
  -> SHA256 完整性检查
  -> PdfLoader（解析与标准化）
  -> DocumentChunker（Chunking）
  -> Dense Encoding + Sparse Encoding
  -> ChromaDB Vector Store + BM25 Index
  -> Named Collection
```

`examples/salon/knowledge_sources/` 中保留 Markdown 维护源，`examples/salon/generated_pdfs/` 是当前真实 ingestion 输入。CLI 目前不会直接发现 `.md` 文件。

## 查询与混合检索流程

```text
MCP Client
  -> stdio JSON-RPC
  -> query_knowledge_hub
  -> Query Processing
  -> Dense Retrieval + BM25
  -> RRF
  -> Retrieved Context + Citations
```

检索服务返回排序后的上下文和来源信息。是否进一步调用 LLM、如何组织最终回答、是否允许检索结果影响业务流程，由 Consumer Application 自己决定。

## MCP Tools

| Tool | 参数 | 用途 |
| --- | --- | --- |
| `query_knowledge_hub` | `query` 必填；`top_k`、`collection` 可选 | 在指定 collection 中执行混合检索并返回文本结果与 Citations。`top_k` 默认 5，范围 1—20。 |
| `list_collections` | `include_stats` 可选，默认 `true` | 列出可用 collection；可包含 chunk / document count 和 metadata。 |
| `get_document_summary` | `doc_id` 必填；`collection` 可选 | 返回指定文档的 title、summary、tags、source path、chunk count 和 metadata。 |

`query_knowledge_hub` 调用示例：

```json
{
  "query": "What is this collection about?",
  "top_k": 4,
  "collection": "knowledge_hub"
}
```

## Collection 设计

collection 是命名知识集合，也是检索和运行时索引的选择边界，例如：

- `knowledge_hub`：默认通用 collection；
- `salon_knowledge`：`examples/salon/` 显式使用的示例 collection；
- Consumer Application 可以传入自己的 collection 名称。

这里的 collection isolation 是索引和查询范围隔离，不代表已经实现认证、授权、租户安全或 production multi-tenancy。

## 技术栈

- Python 3.11
- Official MCP Python SDK
- ChromaDB
- BM25、jieba、RRF
- OpenAI-compatible Embedding Provider（示例配置支持 Qwen）
- MarkItDown PDF loader
- pytest

## 项目结构

```text
mcp-knowledge-service/
├── src/
│   ├── core/               # Query、RRF、response 与 trace
│   ├── ingestion/          # Chunking、encoding 与索引写入
│   ├── libs/               # Loader、Embedding、Vector Store 抽象
│   ├── mcp_server/         # stdio MCP Server 与三个 tools
│   └── observability/      # stderr logger
├── scripts/                # ingest、query、evaluate
├── tests/                  # unit、integration、e2e
├── examples/salon/         # salon 示例知识源与 PDF
├── config/settings.example.yaml
├── docs/
├── architecture.svg
└── pyproject.toml
```

## 快速开始

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
```

真实执行 Embedding 或 Provider 驱动的 ingestion 前，在本地 `.env` 或 shell 环境中配置私有 Key；不要提交 `.env` 或 `config/settings.yaml`。

MCP Server 入口：

```bash
python -m src.mcp_server.server
```

该命令启动 stdio JSON-RPC Server，不是交互式 CLI。正常集成时由 MCP Client 作为独立子进程拉起；单独验证需要 MCP Client 或验证脚本发送 `initialize`、`tools/list` 和 tool call。`stdout` 只用于 MCP 协议消息，日志写入 `stderr`。

## 配置说明

主要本地配置位于 `.env` 与 `config/settings.yaml`：

| 配置 | 作用 |
| --- | --- |
| `DASHSCOPE_API_KEY` | Qwen Provider 的本地凭据；公开示例保持空值。 |
| `DASHSCOPE_BASE_URL` | OpenAI-compatible endpoint。 |
| `DASHSCOPE_EMBEDDING_MODEL` | Embedding model。 |
| `vector_store.persist_directory` | ChromaDB 本地运行目录。 |
| `vector_store.collection_name` | 未显式传参时的默认 collection。 |
| `retrieval.dense_top_k`、`sparse_top_k`、`fusion_top_k` | 两路召回和融合结果数量。 |
| `retrieval.rrf_k` | RRF 平滑参数。 |
| `ingestion.chunk_size`、`chunk_overlap` | Chunking 参数。 |

## Ingestion 示例

导入指定 PDF 或目录：

```bash
python scripts/ingest.py \
  --path <PDF_OR_DIRECTORY> \
  --collection knowledge_hub \
  --force
```

只检查待处理文件，不写入 runtime data：

```bash
python scripts/ingest.py \
  --path <PDF_OR_DIRECTORY> \
  --collection knowledge_hub \
  --dry-run
```

Salon 示例显式使用 `salon_knowledge`：

```bash
python scripts/ingest.py \
  --path examples/salon/generated_pdfs \
  --collection salon_knowledge \
  --force
```

## MCP Client 接入示例

```python
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command="<PATH_TO_SERVICE>/.venv/bin/python",
    args=["-m", "src.mcp_server.server"],
    cwd="<PATH_TO_SERVICE>",
    env=dict(os.environ),
)

async with stdio_client(params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            "query_knowledge_hub",
            {
                "query": "What does the policy say?",
                "top_k": 4,
                "collection": "knowledge_hub",
            },
        )
```

调用方应检查 `CallToolResult.isError`，解析文本与 References，并保留 Citations。

## 测试与历史评估结果

静态依赖与本地测试命令：

```bash
.venv/bin/python -m pip check
.venv/bin/python -m pytest
```

真实 MCP 集成验证需要本地 Provider、已导入的 runtime data 和 MCP Client，流程为：

```text
initialize -> tools/list -> query_knowledge_hub
```

已保存的历史 ingestion 说明记录了 salon 示例的 7 个 PDF、24 个 chunks、24 个 vectors 和 24 个 BM25 documents；本次 README 修改未重新执行 ingestion。该结果只说明示例数据链路和索引规模，不是通用检索质量 benchmark。

仓库内未保存 salon 检索集的 Hit@1、Hit@3 或 MRR 结果，因此本 README 不声明这些指标。构建检索 Golden Dataset 和计算指标的方法见 [检索评估](docs/EVALUATION.md)。

## 故障边界

- MCP 进程未启动、stdio 中断或 tool call 失败：Consumer Application 应将知识检索视为不可用，不应伪造检索结果。
- collection 不存在或尚未 ingestion：`query_knowledge_hub` 返回空结果或带 `isError` 的错误内容，调用方必须显式处理。
- Embedding Provider 配置缺失：需要向量编码的 ingestion 或 Dense Retrieval 无法正常初始化；不会自动获得真实 embedding。
- ChromaDB 或 BM25 runtime index 不可用：检索结果可能为空或 tool 返回错误，runtime data 需要在本地重建。
- 普通日志写入 `stdout` 会污染 MCP JSON-RPC；服务入口将日志导向 `stderr`。
- 本服务不负责预约、价格、排班、库存或交易成功等业务裁决。

## 项目边界与已知限制

- 当前 CLI 直接支持 PDF ingestion；Markdown 是示例中的可维护源文件，不声明直接 `.md` ingestion。
- runtime ChromaDB、BM25、SQLite、日志和 trace 不提交 Git，使用者需要本地导入。
- 当前公开范围不声明 Rerank、Ragas、Graph RAG、Memory、multimodal、Vision、认证授权、production multi-tenancy、自动扩缩容或生产部署。
- collection 提供命名隔离，不等同于安全租户隔离。
- 历史 ingestion 数量来自仓库已有记录，不能解释为本次现场验证或生产性能指标。

## 示例集成

- [AI Hair Salon Agent](https://github.com/hyh0620/ai-hair-salon-agent)：参考 Consumer Application，通过 MCP Client 调用 `salon_knowledge`。
- [`examples/salon/`](examples/salon/README.md)：示例知识源、生成 PDF 和 ingestion 说明；不是根服务默认领域。

## 相关文档

- [系统架构（Architecture）](docs/ARCHITECTURE.md)
- [文档导入（Ingestion）](docs/INGESTION.md)
- [MCP Client 接入（Integration）](docs/INTEGRATION.md)
- [检索评估（Evaluation）](docs/EVALUATION.md)

## 安全说明

不要提交 `.env`、API Key、`config/settings.yaml`、ChromaDB、BM25 index、SQLite runtime data、日志、trace 或本地报告。当前公开项目不声明认证、授权、租户安全或生产级安全控制。
