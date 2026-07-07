# Salon Example / Salon 示例

This example demonstrates how AI Hair Salon Agent uses MCP Knowledge Service with a domain-specific collection.

本示例展示 AI Hair Salon Agent 如何通过指定 collection 接入 MCP Knowledge Service。

## Collection / Collection

```text
salon_knowledge
```

`salon_knowledge` is explicitly selected by the example. It is not the default domain of the root service.

`salon_knowledge` 是示例显式指定的 collection，不是根服务默认业务领域。

## Source Files / 知识源文件

Markdown sources live in `knowledge_sources/`. Generated PDFs live in `generated_pdfs/` and are used as ingestion input for the verified example.

可维护源文件在 `knowledge_sources/`，用于导入验证的 PDF 在 `generated_pdfs/`。

## Ingest / 导入

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

## Query / 查询

```bash
python scripts/query.py \
  --query "染发前后有什么注意事项？" \
  --collection salon_knowledge \
  --top-k 4
```

## Runtime Data / 运行时数据

Ingestion creates local runtime data such as ChromaDB files and BM25 indexes. Do not commit those files.

导入会生成 ChromaDB、BM25 index 等本地运行时数据，不要提交到 Git。
