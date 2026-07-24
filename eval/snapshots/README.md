# Verified Evaluation Snapshots

This directory is reserved for redacted snapshots produced by a real retrieval
run against a versioned corpus and labelled dataset.

A snapshot is not valid merely because its JSON is well formed. Before adding
one, run:

```bash
python scripts/verify_evaluation_snapshot.py eval/snapshots/<snapshot>.json
```

Do not commit raw reports, local paths, credentials, runtime databases, vector
stores, traces, or copied metrics from a consumer application.
