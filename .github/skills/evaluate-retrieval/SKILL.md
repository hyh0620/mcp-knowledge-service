---
name: evaluate-retrieval
description: Evaluate retrieval quality for a specified collection with a golden test set.
---

# Evaluate Retrieval

## Inputs

- Collection name.
- Golden test set with query and expected source.

## Pipeline

1. Confirm collection exists:
   ```bash
   python scripts/query.py --query "health check" --collection <COLLECTION> --top-k 1
   ```
2. Run retrieval cases using the project evaluation script or a small client script.
3. For each case record:
   - returned sources
   - first relevant rank
   - citation count
   - latency
4. Compute:
   - Hit@1
   - Hit@3
   - MRR
   - citation expected-source match

## Rules

- Report numerator and denominator.
- Do not claim Rerank or Ragas unless actually enabled and verified.
- Do not use LLM subjective scoring as retrieval accuracy.
