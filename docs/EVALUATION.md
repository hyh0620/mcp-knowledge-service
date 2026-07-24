# Retrieval Evaluation / 检索评估

检索评估使用带 Ground Truth 的版本化数据集。功能流程、检索质量和消费者侧答案质量是不同问题，报告中不得混为一个“准确率”。

## 数据集定位

- `tests/fixtures/golden_test_set.json` 是加载与流程测试使用的 sample/template。它没有 chunk 或 source Ground Truth，因此不产生 Hit@K 或 MRR，也不代表检索 Benchmark。
- `eval/datasets/salon_retrieval.jsonl` 是 salon 示例语料的来源级数据集。每条样本包含稳定 ID、query、collection 和 `expected_sources`。
- `expected_chunk_ids` 与 `expected_sources` 可以单独或同时提供；报告分别计算 chunk-level 与 source-level 指标。
- 两类 Ground Truth 都为空时，样本状态为 `not_evaluated`，不进入 Hit@K 或 MRR 分母。

## 指标语义

| Metric | 计算方式 |
| --- | --- |
| Chunk Hit@K | 前 K 个返回 chunk 中是否存在任一 expected chunk ID |
| Chunk MRR | 第一个 expected chunk 的 reciprocal rank |
| Source Hit@K | 按 Citation 顺序，前 K 个唯一来源中是否存在 expected source |
| Source MRR | expected source 第一次出现的 reciprocal rank |
| Citation presence | 最终返回是否包含 Citation |
| Citation expected-source match | 最终 Citation 是否包含 expected source |
| Empty-result handling | 标记为 `expect_empty_result` 的样本是否返回空结果 |

Source 比较只使用规范化文件名。相同 PDF 的多个 chunk 在来源级排名中只出现一次，因此不会重复提高来源命中。真正有 Ground Truth 但未命中的样本记为 0；没有 Ground Truth 的样本记为 `not_evaluated`。

聚合项都保存：

```json
{
  "numerator": 7.0,
  "denominator": 8,
  "rate": 0.875
}
```

分母为 0 时 `rate` 为 `null`。

## 当前独立 Salon 检索结果

2026-07-24 使用本仓库 `salon_knowledge` collection、8 条来源级样本和真实 Embedding Provider 运行：

| 指标 | 结果 |
| --- | ---: |
| Queries | 8 |
| Evaluated | 8 |
| Source Hit@1 | 7 / 8 |
| Source Hit@3 | 8 / 8 |
| Source MRR | 0.9375 |
| Citation expected-source match | 8 / 8 |

这是小型受控语料上的独立检索回归结果，不是生产准确率或通用 Benchmark。对应去敏快照会记录 dataset SHA256、corpus version、模型标识、检索参数、逐样本排名和延迟，并由验证脚本重新计算摘要。

## 运行

示例 fixture（合法但不计算质量分数）：

```bash
python scripts/evaluate.py \
  --no-search \
  --test-set tests/fixtures/golden_test_set.json
```

真实 salon 检索：

```bash
python scripts/evaluate.py \
  --test-set eval/datasets/salon_retrieval.jsonl \
  --collection salon_knowledge \
  --top-k 3
```

生成真实快照时必须提供 corpus version：

```bash
python scripts/evaluate.py \
  --test-set eval/datasets/salon_retrieval.jsonl \
  --collection salon_knowledge \
  --top-k 3 \
  --corpus-version salon-7pdf-24chunks \
  --snapshot eval/snapshots/verified_<UTC_DATE>_<SHORT_SHA>.json
```

验证快照：

```bash
python scripts/verify_evaluation_snapshot.py \
  eval/snapshots/verified_<UTC_DATE>_<SHORT_SHA>.json
```

## 报告规则

- 始终报告总 query、evaluated 和 not_evaluated 数量。
- 分开报告 chunk-level 与 source-level 指标。
- Empty-result case 不进入普通 Hit@K 分母。
- 不用主观 LLM 打分冒充客观检索指标。
- 不提交包含本地路径、凭据、trace、runtime database 或原始敏感响应的报告。
- 快照仅对其记录的 corpus、dataset、collection、Provider model 和参数有效。
