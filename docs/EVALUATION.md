# Retrieval Evaluation / 检索评估

Retrieval evaluation should use a golden dataset with expected source documents.

检索评估应使用带 expected source 的 golden dataset，而不是用主观 LLM 打分冒充客观检索指标。

## Golden Dataset / Golden 数据集

Suggested JSONL shape:

```json
{
  "id": "R001",
  "query": "What is the cancellation policy?",
  "collection": "knowledge_hub",
  "expected_sources": ["policy.pdf"],
  "notes": "Cancellation policy lookup."
}
```

Each case should include the query, target collection, expected source, and any notes needed to interpret the result.

每条样本应包含 query、collection、expected source 和必要说明。

## Metrics / 指标

| Metric | Meaning | 中文说明 |
| --- | --- | --- |
| Hit@1 | Expected source appears at rank 1. | 预期来源出现在第一名。 |
| Hit@3 | Expected source appears in top 3. | 预期来源出现在前三名。 |
| MRR | Mean reciprocal rank of expected source. | 预期来源排名倒数的平均值。 |
| Citation presence rate | Results include citations. | 返回结果包含 citations。 |
| Citation expected-source match rate | Expected source appears in citations. | citations 中出现预期来源。 |
| Empty-result handling | Missing collection or no-result cases do not produce false citations. | 空结果或缺失 collection 不应伪造来源。 |

## Reporting Rules / 报告规则

- Always report sample count.
- Keep Functional Contract results separate from Retrieval Quality results.
- Do not use subjective LLM scoring as objective retrieval quality.
- Do not claim production accuracy from a small controlled corpus.
- Keep raw local reports out of Git if they contain local paths, trace IDs, or environment details.

报告必须写明样本数，区分功能契约和检索质量，不把小型受控语料结果写成生产准确率或通用 benchmark。

## Reproducibility / 可复现性

Evaluation should record:

- collection
- corpus version
- embedding provider/model identifier
- sample count
- Hit@1, Hit@3, MRR
- citation match counts
- empty-result handling counts

评估结果应能从指定 collection、语料版本和样本集复现，但不应提交包含本地路径或敏感环境信息的原始运行报告。
