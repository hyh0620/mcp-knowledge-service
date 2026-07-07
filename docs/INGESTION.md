# Ingestion / 知识导入

The ingestion pipeline converts source documents into retrievable collection data.

知识导入流程把源文档转换为指定 collection 下的可检索数据。

## Command / 命令

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection <COLLECTION_NAME> \
  --force
```

Dry run:

```bash
python scripts/ingest.py \
  --path <SOURCE_PATH> \
  --collection <COLLECTION_NAME> \
  --dry-run
```

## Inputs / 输入

- `--path`: source file or directory.
- `--collection`: target collection name.
- `--force`: replace or refresh existing collection data where supported.
- `--dry-run`: inspect planned work without writing runtime data.

`--path` 指向知识源文件或目录；`--collection` 指定目标 collection。`--dry-run` 用于预检查，不写入运行时数据。

## Outputs / 输出

The pipeline reports:

- processed files
- failed files
- generated chunks
- stored vectors
- BM25 indexed documents

输出应关注 file、chunk、vector 和 BM25 document 数量，以及失败文件。

## Collection Names / Collection 名称

Pass collection names explicitly. Do not rely on a business-specific default.

collection 应显式传入；不要依赖某个业务领域默认值。

## Salon Example / Salon 示例

```bash
python scripts/ingest.py \
  --path examples/salon/generated_pdfs \
  --collection salon_knowledge \
  --force
```

The salon example is a reference integration for AI Hair Salon Agent. It is not the default domain of this service.

salon 示例只是 AI Hair Salon Agent 的参考集成，不是根服务默认领域。

## Runtime Data / 运行时数据

Runtime output under `data/`, ChromaDB files, BM25 indexes, SQLite files, logs, traces, and local reports should not be committed.

`data/`、ChromaDB、BM25 index、SQLite、日志、trace 和本地报告不提交到 Git。
