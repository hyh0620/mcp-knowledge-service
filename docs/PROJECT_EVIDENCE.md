# 项目证据索引

本文把可用于简历或面试的项目表述与代码、验证命令和当前限制对应起来。它用于核验实现，不替代源码和测试结果。

## 项目定位

MCP Knowledge Service 是独立知识检索服务。它负责文档摄取、Dense/BM25 混合检索、RRF 排序和 Citations；Consumer Application 负责使用检索结果组织回答和执行业务流程。

## 证据表

| 简历可用表述 | 代码或文档位置 | 验证命令 | 当前限制 |
| --- | --- | --- | --- |
| 使用 Official MCP Python SDK 实现 stdio MCP Server，支持 JSON-RPC initialize、tools/list 和 tools/call | `src/mcp_server/server.py`、`src/mcp_server/protocol_handler.py` | `python -m pytest tests/e2e/test_mcp_client.py tests/integration/test_mcp_server.py` | 当前公开入口为 stdio，不声明远程 transport |
| 提供 `query_knowledge_hub`、`list_collections`、`get_document_summary` 三个 Tools | `src/mcp_server/tools/` | `python -m pytest tests/unit/test_query_processor.py tests/unit/test_list_collections.py tests/unit/test_get_document_summary.py` | Tool 不承担上层业务决策 |
| PDF 摄取链路包含 SHA256 完整性检查、解析、Chunking、Embedding 和索引写入 | `src/ingestion/`、`src/libs/loader/` | `python -m pytest tests/e2e/test_data_ingestion.py tests/unit/test_file_integrity.py tests/unit/test_document_chunker.py` | CLI 当前直接发现 PDF；Markdown 是示例维护源 |
| 使用 ChromaDB 保存 Dense vectors，使用 BM25 建立关键词索引 | `src/libs/vector_store/`、`src/ingestion/storage/bm25_indexer.py` | `python -m pytest tests/integration/test_chroma_store_roundtrip.py tests/unit/test_bm25_indexer_roundtrip.py` | runtime vector/index data 不提交 Git |
| 使用 RRF 融合 Dense 与 BM25 排名 | `src/core/query_engine/hybrid_search.py`、`src/core/query_engine/fusion.py` | `python -m pytest tests/integration/test_hybrid_search.py tests/unit/test_fusion_rrf.py` | 当前没有 Cross-Encoder Reranker |
| 返回有序 Citations，并保留稳定 source 与 chunk 关联 | `src/core/response/citation_generator.py`、`src/core/response/response_builder.py` | `python -m pytest tests/unit/test_response_builder.py` | Citation 质量依赖摄取 metadata |
| Dense 或 Sparse 单路失败时可降级到可用路径 | `src/core/query_engine/hybrid_search.py` | `python -m pytest tests/integration/test_hybrid_search.py` | 两路都失败时返回明确错误 |
| 协议输出与日志分离，避免 stdout 污染 stdio JSON-RPC | `src/mcp_server/server.py`、`src/observability/logger.py` | `python -m pytest tests/e2e/test_mcp_client.py tests/unit/test_jsonl_logger.py` | 不等同于完整生产可观测平台 |
| 测试分为 unit、integration 与 e2e | `tests/unit/`、`tests/integration/`、`tests/e2e/` | `python -m pytest` | 部分真实 Provider 测试按环境条件跳过 |
| 评估框架区分 chunk/source Ground Truth、无标注样本和空结果 | `src/libs/evaluator/custom_evaluator.py`、`src/observability/evaluation/eval_runner.py` | `python -m pytest tests/unit/test_custom_evaluator.py tests/unit/test_eval_runner.py` | 示例 fixture 不是质量 Benchmark |
| 去敏快照可从逐用例结果重算 Hit@K 与 MRR | `src/observability/evaluation/snapshot.py`、`scripts/verify_evaluation_snapshot.py` | `python -m pytest tests/unit/test_evaluation_snapshot.py` | 快照只对记录的 corpus、dataset 和配置有效 |

## 当前不能使用的表述

仓库当前没有实现或验证 Cross-Encoder、Ragas、Redis、远程 MCP transport、生产多租户、多模态摄取、万级文档规模、生产流量或商业准确率。Collection 是检索范围边界，不是安全租户边界。
