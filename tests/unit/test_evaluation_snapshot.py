"""Tests for redacted evaluation snapshot generation and verification."""

from __future__ import annotations

import copy
from types import SimpleNamespace

import pytest

from src.libs.evaluator.custom_evaluator import CustomEvaluator
from src.observability.evaluation.eval_runner import EvalReport, EvalRunner, QueryResult
from src.observability.evaluation.snapshot import (
    build_snapshot,
    load_and_verify_snapshot,
    verify_snapshot,
    write_snapshot,
)


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        llm=SimpleNamespace(model="example-chat-model"),
        embedding=SimpleNamespace(model="example-embedding-model"),
        ingestion=SimpleNamespace(
            splitter="recursive",
            chunk_size=650,
            chunk_overlap=80,
        ),
        retrieval=SimpleNamespace(
            dense_top_k=20,
            sparse_top_k=20,
            fusion_top_k=10,
            rrf_k=60,
        ),
    )


def _report() -> EvalReport:
    metrics = CustomEvaluator().evaluate(
        "q",
        [
            {
                "id": "c1",
                "metadata": {"source_path": "/private/corpus/policy.pdf"},
            }
        ],
        ground_truth={
            "expected_chunk_ids": ["c1"],
            "expected_sources": ["/expected/policy.pdf"],
        },
        top_k=3,
    )
    result = QueryResult(
        query="q",
        case_id="R1",
        expected_chunk_ids=["c1"],
        expected_sources=["policy.pdf"],
        retrieved_chunk_ids=["c1"],
        returned_sources=["policy.pdf"],
        evaluation_status="evaluated",
        metrics=metrics,
        elapsed_ms=12.5,
    )
    return EvalReport(
        query_results=[result],
        aggregate_metrics=EvalRunner._aggregate_metrics([result]),
        summary={
            "total_queries": 1,
            "evaluated_queries": 1,
            "not_evaluated_queries": 0,
            "empty_result_cases": 0,
        },
    )


def test_snapshot_round_trip_and_redaction(tmp_path) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text('{"test_cases":[]}', encoding="utf-8")
    snapshot = build_snapshot(
        _report(),
        dataset_path=dataset,
        git_commit_sha="a" * 40,
        corpus_version="corpus-v1",
        collection="knowledge",
        settings=_settings(),
    )
    output = write_snapshot(snapshot, tmp_path / "snapshot.json")

    verified = load_and_verify_snapshot(output)

    assert verified["query_count"] == 1
    assert verified["evaluated_count"] == 1
    assert verified["query_results"][0]["returned_sources"] == ["policy.pdf"]
    rendered = output.read_text(encoding="utf-8")
    assert "/private/" not in rendered
    assert "generated_answer" not in rendered
    assert "trace" not in rendered.casefold()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("query_count", 2, "query_count"),
        ("evaluated_count", 0, "evaluated_count"),
        ("dataset_sha256", "bad", "dataset_sha256"),
    ],
)
def test_snapshot_rejects_inconsistent_summary(
    tmp_path,
    field: str,
    value,
    message: str,
) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text("{}", encoding="utf-8")
    snapshot = build_snapshot(
        _report(),
        dataset_path=dataset,
        git_commit_sha="b" * 40,
        corpus_version="corpus-v1",
        collection="knowledge",
        settings=_settings(),
    )
    broken = copy.deepcopy(snapshot)
    broken[field] = value

    with pytest.raises(ValueError, match=message):
        verify_snapshot(broken)


def test_snapshot_recomputes_aggregates(tmp_path) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text("{}", encoding="utf-8")
    snapshot = build_snapshot(
        _report(),
        dataset_path=dataset,
        git_commit_sha="c" * 40,
        corpus_version="corpus-v1",
        collection="knowledge",
        settings=_settings(),
    )
    snapshot["aggregate_metrics"]["source_level"]["mrr"]["rate"] = 0.25

    with pytest.raises(ValueError, match="aggregate_metrics"):
        verify_snapshot(snapshot)


def test_snapshot_rejects_source_paths(tmp_path) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text("{}", encoding="utf-8")
    snapshot = build_snapshot(
        _report(),
        dataset_path=dataset,
        git_commit_sha="d" * 40,
        corpus_version="corpus-v1",
        collection="knowledge",
        settings=_settings(),
    )
    snapshot["query_results"][0]["returned_sources"] = ["/private/policy.pdf"]

    with pytest.raises(ValueError, match="public source"):
        verify_snapshot(snapshot)
