"""Build and verify redacted, reproducible retrieval evaluation snapshots."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.libs.evaluator.custom_evaluator import CustomEvaluator
from src.observability.evaluation.eval_runner import EvalReport, EvalRunner, QueryResult

SCHEMA_VERSION = "1.0"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build_snapshot(
    report: EvalReport,
    *,
    dataset_path: str | Path,
    git_commit_sha: str,
    corpus_version: str,
    collection: str,
    settings: Any,
) -> dict[str, Any]:
    """Build a public snapshot without prompts, answers, paths, or credentials."""
    if not git_commit_sha.strip():
        raise ValueError("git_commit_sha is required")
    if not corpus_version.strip():
        raise ValueError("corpus_version is required")
    if not collection.strip():
        raise ValueError("collection is required")

    query_results = [_public_query_result(result) for result in report.query_results]
    latencies = sorted(result.elapsed_ms for result in report.query_results)
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit_sha": git_commit_sha,
        "dataset_sha256": sha256_file(dataset_path),
        "corpus_version": corpus_version,
        "collection": collection,
        "query_count": len(query_results),
        "evaluated_count": sum(
            item["evaluation_status"] == "evaluated" for item in query_results
        ),
        "not_evaluated_count": sum(
            item["evaluation_status"] == "not_evaluated" for item in query_results
        ),
        "model_identifier": getattr(getattr(settings, "llm", None), "model", None),
        "embedding_model_identifier": getattr(
            getattr(settings, "embedding", None),
            "model",
            None,
        ),
        "chunking": _settings_values(
            getattr(settings, "ingestion", None),
            ("splitter", "chunk_size", "chunk_overlap"),
        ),
        "retrieval": _settings_values(
            getattr(settings, "retrieval", None),
            ("dense_top_k", "sparse_top_k", "fusion_top_k", "rrf_k"),
        ),
        "aggregate_metrics": report.aggregate_metrics,
        "latency": {
            "sample_count": len(latencies),
            "p50_ms": _percentile(latencies, 0.50),
            "p95_ms": _percentile(latencies, 0.95),
        },
        "query_results": query_results,
    }
    verify_snapshot(snapshot)
    return snapshot


def write_snapshot(snapshot: dict[str, Any], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output


def verify_snapshot(snapshot: dict[str, Any]) -> None:
    """Recompute all aggregates and reject inconsistent or unsafe snapshots."""
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported snapshot schema_version")
    if not SHA256_PATTERN.fullmatch(str(snapshot.get("dataset_sha256", ""))):
        raise ValueError("dataset_sha256 must be a lowercase SHA-256 digest")

    query_results = snapshot.get("query_results")
    if not isinstance(query_results, list):
        raise ValueError("query_results must be a list")
    if snapshot.get("query_count") != len(query_results):
        raise ValueError("query_count does not match query_results")

    evaluated_count = sum(
        item.get("evaluation_status") == "evaluated" for item in query_results
    )
    not_evaluated_count = sum(
        item.get("evaluation_status") == "not_evaluated" for item in query_results
    )
    if snapshot.get("evaluated_count") != evaluated_count:
        raise ValueError("evaluated_count does not match query_results")
    if snapshot.get("not_evaluated_count") != not_evaluated_count:
        raise ValueError("not_evaluated_count does not match query_results")
    if evaluated_count + not_evaluated_count != len(query_results):
        raise ValueError("query_results contain an invalid evaluation_status")

    reconstructed = [_recompute_query_result(item) for item in query_results]
    recomputed = EvalRunner._aggregate_metrics(reconstructed)
    if not _equal_numbers(snapshot.get("aggregate_metrics"), recomputed):
        raise ValueError("aggregate_metrics do not match query_results")

    for item in query_results:
        for field_name in ("expected_sources", "returned_sources"):
            values = item.get(field_name, [])
            if not isinstance(values, list):
                raise ValueError(f"{field_name} must be a list")
            if any("/" in str(value) or "\\" in str(value) for value in values):
                raise ValueError(f"{field_name} must contain public source identifiers")


def load_and_verify_snapshot(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("snapshot root must be a JSON object")
    verify_snapshot(data)
    return data


def _public_query_result(result: QueryResult) -> dict[str, Any]:
    return {
        "id": result.case_id,
        "category": result.category,
        "expected_chunk_ids": result.expected_chunk_ids,
        "expected_sources": result.expected_sources,
        "returned_chunk_ids": result.retrieved_chunk_ids,
        "returned_sources": result.returned_sources,
        "evaluation_status": result.evaluation_status,
        "metrics": {
            key: value
            for key, value in result.metrics.items()
            if key != "returned_sources"
        },
        "expect_empty_result": result.expect_empty_result,
        "empty_result_handling": result.empty_result_handling,
        "latency_ms": round(result.elapsed_ms, 4),
    }


def _recompute_query_result(item: dict[str, Any]) -> QueryResult:
    expected_chunk_ids = list(item.get("expected_chunk_ids", []))
    expected_sources = list(item.get("expected_sources", []))
    returned_chunk_ids = list(item.get("returned_chunk_ids", []))
    returned_sources = list(item.get("returned_sources", []))
    stored_metrics = item.get("metrics")
    if not isinstance(stored_metrics, dict):
        raise ValueError("query result metrics must be an object")

    level = stored_metrics.get("chunk_level")
    if not isinstance(level, dict):
        level = stored_metrics.get("source_level")
    top_k = level.get("k") if isinstance(level, dict) else None
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("query result metrics require a positive k")

    retrieved_chunks = [
        {
            "id": chunk_id,
            "metadata": {
                "source": (
                    returned_sources[index]
                    if index < len(returned_sources)
                    else ""
                )
            },
        }
        for index, chunk_id in enumerate(returned_chunk_ids)
    ]
    recomputed_metrics = CustomEvaluator().evaluate(
        "snapshot verification query",
        retrieved_chunks,
        ground_truth={
            "expected_chunk_ids": expected_chunk_ids,
            "expected_sources": expected_sources,
        },
        top_k=top_k,
        citation_sources=returned_sources,
    )
    recomputed_metrics.pop("returned_sources", None)
    if not _equal_numbers(stored_metrics, recomputed_metrics):
        raise ValueError("query result metrics do not match expected and returned rankings")

    expect_empty_result = bool(item.get("expect_empty_result", False))
    empty_result_handling = (
        1.0 if expect_empty_result and not returned_chunk_ids else
        0.0 if expect_empty_result else
        None
    )
    if not _equal_numbers(item.get("empty_result_handling"), empty_result_handling):
        raise ValueError("empty_result_handling does not match returned results")

    status = str(recomputed_metrics["evaluation_status"])
    if item.get("evaluation_status") != status:
        raise ValueError("evaluation_status does not match ground truth")

    return QueryResult(
        query="",
        case_id=str(item.get("id", "")),
        category=str(item.get("category", "retrieval")),
        expected_chunk_ids=expected_chunk_ids,
        expected_sources=expected_sources,
        retrieved_chunk_ids=returned_chunk_ids,
        returned_sources=returned_sources,
        evaluation_status=status,
        metrics=recomputed_metrics,
        expect_empty_result=expect_empty_result,
        empty_result_handling=empty_result_handling,
        elapsed_ms=float(item.get("latency_ms", 0.0)),
    )


def _settings_values(settings: Any, names: tuple[str, ...]) -> dict[str, Any]:
    if settings is None:
        return {}
    return {name: getattr(settings, name, None) for name in names}


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    index = max(0, math.ceil(len(values) * fraction) - 1)
    return round(values[index], 4)


def _equal_numbers(left: Any, right: Any) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _equal_numbers(left[key], right[key]) for key in left
        )
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _equal_numbers(a, b) for a, b in zip(left, right)
        )
    return bool(left == right)
