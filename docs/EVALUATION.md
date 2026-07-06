# Retrieval Evaluation

Retrieval evaluation should use a golden dataset with expected source documents.

## Suggested JSONL Shape

```json
{
  "id": "R001",
  "query": "What is the cancellation policy?",
  "collection": "knowledge_hub",
  "expected_sources": ["policy.pdf"],
  "notes": "Cancellation policy lookup."
}
```

## Metrics

- Hit@1: expected source appears at rank 1.
- Hit@3: expected source appears in top 3.
- MRR: mean reciprocal rank of expected source.
- Citation presence rate: result includes citations.
- Citation expected-source match rate: expected source appears in citations.
- Empty-result handling: missing collection or no-result cases do not produce false citations.

## Rules

- Always report sample count.
- Do not use subjective LLM scoring as objective retrieval quality.
- Do not claim Rerank or Ragas results unless they were actually run.
- Keep raw local reports out of git if they contain local paths, trace IDs, or environment details.
