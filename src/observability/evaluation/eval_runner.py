"""Evaluation runner for batch quality assessment.

EvalRunner reads a golden test set, runs HybridSearch for each test case,
optionally generates answers, then invokes the configured Evaluator(s) to
produce a structured evaluation report.

Design Principles:
- Config-Driven: Evaluator selected via settings.yaml.
- Observable: Produces EvalReport with per-query details.
- Decoupled: Works with any BaseEvaluator implementation.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from src.libs.evaluator.base_evaluator import BaseEvaluator

logger = logging.getLogger(__name__)


@dataclass
class GoldenTestCase:
    """A single evaluation test case from the golden test set.

    Attributes:
        query: The test query string.
        expected_chunk_ids: Ground-truth chunk IDs for IR metrics.
        expected_sources: Ground-truth source file names (optional).
        reference_answer: Reference answer text for LLM-as-Judge (optional).
    """

    query: str
    case_id: str = ""
    category: str = "retrieval"
    expected_chunk_ids: list[str] = field(default_factory=list)
    expected_sources: list[str] = field(default_factory=list)
    reference_answer: str | None = None
    expect_empty_result: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoldenTestCase:
        query = data.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("each evaluation case requires a non-empty query")
        expected_chunk_ids = data.get("expected_chunk_ids", [])
        expected_sources = data.get("expected_sources", [])
        if not isinstance(expected_chunk_ids, list):
            raise ValueError("expected_chunk_ids must be a list")
        if not isinstance(expected_sources, list):
            raise ValueError("expected_sources must be a list")
        return cls(
            case_id=str(data.get("id", "")),
            category=str(data.get("category", "retrieval")),
            query=query,
            expected_chunk_ids=expected_chunk_ids,
            expected_sources=expected_sources,
            reference_answer=data.get("reference_answer"),
            expect_empty_result=bool(data.get("expect_empty_result", False)),
        )


@dataclass
class QueryResult:
    """Result of evaluating a single test case.

    Attributes:
        query: The test query.
        retrieved_chunk_ids: IDs of chunks actually retrieved.
        generated_answer: The generated answer (if applicable).
        metrics: Evaluation metrics for this query.
        elapsed_ms: Time taken for retrieval + evaluation.
    """

    query: str
    case_id: str = ""
    category: str = "retrieval"
    expected_chunk_ids: list[str] = field(default_factory=list)
    expected_sources: list[str] = field(default_factory=list)
    retrieved_chunk_ids: list[str] = field(default_factory=list)
    returned_sources: list[str] = field(default_factory=list)
    generated_answer: str | None = None
    evaluation_status: str = "not_evaluated"
    metrics: dict[str, Any] = field(default_factory=dict)
    expect_empty_result: bool = False
    empty_result_handling: float | None = None
    elapsed_ms: float = 0.0


@dataclass
class EvalReport:
    """Aggregated evaluation report across all test cases.

    Attributes:
        query_results: Per-query evaluation results.
        aggregate_metrics: Averaged metrics across all queries.
        total_elapsed_ms: Total time for the entire evaluation.
        evaluator_name: Name of the evaluator used.
        test_set_path: Path to the golden test set file.
    """

    query_results: list[QueryResult] = field(default_factory=list)
    aggregate_metrics: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, int] = field(default_factory=dict)
    total_elapsed_ms: float = 0.0
    evaluator_name: str = ""
    test_set_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialise report to dictionary."""
        return cast(dict[str, Any], _round_floats({
            "evaluator_name": self.evaluator_name,
            "test_set_path": self.test_set_path,
            "total_elapsed_ms": self.total_elapsed_ms,
            "summary": self.summary,
            "aggregate_metrics": self.aggregate_metrics,
            "query_count": len(self.query_results),
            "query_results": [
                {
                    "id": qr.case_id,
                    "category": qr.category,
                    "query": qr.query,
                    "expected_chunk_ids": qr.expected_chunk_ids,
                    "expected_sources": qr.expected_sources,
                    "retrieved_chunk_ids": qr.retrieved_chunk_ids,
                    "returned_sources": qr.returned_sources,
                    "generated_answer": qr.generated_answer,
                    "evaluation_status": qr.evaluation_status,
                    "metrics": qr.metrics,
                    "expect_empty_result": qr.expect_empty_result,
                    "empty_result_handling": qr.empty_result_handling,
                    "elapsed_ms": qr.elapsed_ms,
                }
                for qr in self.query_results
            ],
        }))


def _round_floats(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, dict):
        return {key: _round_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_round_floats(item) for item in value]
    return value


def load_test_set(path: str | Path) -> list[GoldenTestCase]:
    """Load golden test set from a JSON file.

    Args:
        path: Path to the golden test set JSON file.

    Returns:
        List of TestCase instances.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Golden test set not found: {file_path}")

    if file_path.suffix.casefold() == ".jsonl":
        cases: list[GoldenTestCase] = []
        for line_number, raw_line in enumerate(
            file_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not raw_line.strip():
                continue
            try:
                data = json.loads(raw_line)
                if not isinstance(data, dict):
                    raise ValueError("case must be a JSON object")
                cases.append(GoldenTestCase.from_dict(data))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid JSONL evaluation case at line {line_number}: {exc}"
                ) from exc
        return cases

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "test_cases" not in data:
        raise ValueError(
            "Invalid golden test set format: missing 'test_cases' key."
        )

    return [GoldenTestCase.from_dict(tc) for tc in data["test_cases"]]


class EvalRunner:
    """Runs batch evaluation against a golden test set.

    This class orchestrates:
    1. Loading the golden test set
    2. Running HybridSearch for each query
    3. Optionally generating answers
    4. Invoking the evaluator to score each result
    5. Aggregating metrics into an EvalReport

    Example::

        runner = EvalRunner(
            settings=settings,
            hybrid_search=hybrid_search,
            evaluator=evaluator,
        )
        report = runner.run("tests/fixtures/golden_test_set.json")
        print(report.aggregate_metrics)
    """

    def __init__(
        self,
        settings: Any = None,
        hybrid_search: Any = None,
        evaluator: BaseEvaluator | None = None,
        answer_generator: Any = None,
        answer_overrides: dict[int, str] | None = None,
    ) -> None:
        """Initialize EvalRunner.

        Args:
            settings: Application settings.
            hybrid_search: HybridSearch instance for retrieval.
            evaluator: BaseEvaluator instance for scoring.
            answer_generator: Optional callable(query, chunks) -> str
                for generating answers. If None, a simple concatenation
                is used as a placeholder.
            answer_overrides: Optional dict mapping test case index (0-based)
                to a user-provided answer string. When present, the override
                answer is used instead of auto-generation for that test case.
        """
        self.settings = settings
        self.hybrid_search = hybrid_search
        self.evaluator = evaluator
        self.answer_generator = answer_generator
        self.answer_overrides = answer_overrides or {}

    def run(
        self,
        test_set_path: str | Path,
        top_k: int = 10,
        collection: str | None = None,
    ) -> EvalReport:
        """Run evaluation on the golden test set.

        Args:
            test_set_path: Path to golden_test_set.json.
            top_k: Number of chunks to retrieve per query.
            collection: Optional collection name filter.

        Returns:
            EvalReport with per-query and aggregate metrics.

        Raises:
            FileNotFoundError: If test set file doesn't exist.
            ValueError: If evaluator or hybrid_search is not set.
        """
        if self.evaluator is None:
            raise ValueError("EvalRunner requires an evaluator.")

        test_cases = load_test_set(test_set_path)
        if not test_cases:
            raise ValueError("Golden test set is empty.")

        logger.info(
            "Starting evaluation: %d test cases, evaluator=%s",
            len(test_cases),
            type(self.evaluator).__name__,
        )

        report = EvalReport(
            evaluator_name=type(self.evaluator).__name__,
            test_set_path=str(test_set_path),
        )

        t0 = time.monotonic()

        for idx, tc in enumerate(test_cases):
            logger.info("Evaluating [%d/%d]: %s", idx + 1, len(test_cases), tc.query[:60])
            # Use user-provided answer override if available for this index
            answer_override = self.answer_overrides.get(idx)
            qr = self._evaluate_single(
                tc, top_k=top_k, collection=collection,
                answer_override=answer_override,
            )
            report.query_results.append(qr)

        report.total_elapsed_ms = (time.monotonic() - t0) * 1000.0
        report.aggregate_metrics = self._aggregate_metrics(report.query_results)
        report.summary = {
            "total_queries": len(report.query_results),
            "evaluated_queries": sum(
                result.evaluation_status == "evaluated"
                for result in report.query_results
            ),
            "not_evaluated_queries": sum(
                result.evaluation_status == "not_evaluated"
                for result in report.query_results
            ),
            "empty_result_cases": sum(
                result.expect_empty_result for result in report.query_results
            ),
        }

        logger.info(
            "Evaluation complete: %d queries, aggregate=%s",
            len(report.query_results),
            report.aggregate_metrics,
        )

        return report

    def _evaluate_single(
        self,
        test_case: GoldenTestCase,
        top_k: int = 10,
        collection: str | None = None,
        answer_override: str | None = None,
    ) -> QueryResult:
        """Evaluate a single test case.

        Args:
            test_case: The test case to evaluate.
            top_k: Number of results to retrieve.
            collection: Optional collection filter.
            answer_override: User-provided answer text. When set, used
                instead of auto-generated answer from chunks.

        Returns:
            QueryResult with metrics for this test case.
        """
        t0 = time.monotonic()
        qr = QueryResult(
            case_id=test_case.case_id,
            category=test_case.category,
            query=test_case.query,
            expected_chunk_ids=list(test_case.expected_chunk_ids),
            expected_sources=[
                self._normalize_source(source)
                for source in test_case.expected_sources
                if self._normalize_source(source)
            ],
            expect_empty_result=test_case.expect_empty_result,
        )

        # Step 1: Retrieve chunks
        retrieved_chunks = self._retrieve(test_case.query, top_k, collection)
        qr.retrieved_chunk_ids = [
            self._get_chunk_id(c) for c in retrieved_chunks
        ]
        citation_sources = self._get_citation_sources(retrieved_chunks)

        # Step 2: Generate answer — prefer user override, then generator, then fallback
        if answer_override:
            answer = answer_override
        else:
            answer = self._generate_answer(test_case.query, retrieved_chunks)
        qr.generated_answer = answer

        # Step 3: Build ground truth
        ground_truth = {
            "expected_chunk_ids": test_case.expected_chunk_ids,
            "expected_sources": test_case.expected_sources,
        }

        # Step 4: Evaluate
        try:
            metrics = self.evaluator.evaluate(  # type: ignore[union-attr]
                query=test_case.query,
                retrieved_chunks=retrieved_chunks,
                generated_answer=answer,
                ground_truth=ground_truth,
                top_k=top_k,
                citation_sources=citation_sources,
            )
            qr.metrics = metrics
            qr.evaluation_status = str(
                metrics.get(
                    "evaluation_status",
                    (
                        "evaluated"
                        if any(
                            isinstance(metrics.get(name), (int, float))
                            for name in ("hit_rate", "mrr")
                        )
                        else "not_evaluated"
                    ),
                )
            )
            qr.returned_sources = list(metrics.get("returned_sources", []))
        except Exception as exc:
            logger.warning("Evaluation failed for '%s': %s", test_case.query[:40], exc)
            qr.metrics = {}

        if test_case.expect_empty_result:
            qr.empty_result_handling = 1.0 if not retrieved_chunks else 0.0

        qr.elapsed_ms = (time.monotonic() - t0) * 1000.0
        return qr

    def _retrieve(
        self,
        query: str,
        top_k: int,
        collection: str | None,
    ) -> list[Any]:
        """Retrieve chunks using HybridSearch.

        Falls back to an empty list if search is not configured.
        """
        if self.hybrid_search is None:
            logger.warning("No HybridSearch configured; returning empty results.")
            return []

        try:
            results = self.hybrid_search.search(
                query=query,
                top_k=top_k,
            )
            return results if isinstance(results, list) else results.results
        except Exception as exc:
            logger.warning("Retrieval failed for '%s': %s", query[:40], exc)
            return []

    def _generate_answer(self, query: str, chunks: list[Any]) -> str:
        """Generate an answer from retrieved chunks.

        If a custom answer_generator is provided, use it.
        Otherwise, concatenate chunk texts as a simple placeholder.
        """
        if self.answer_generator is not None:
            try:
                return str(self.answer_generator(query, chunks))
            except Exception as exc:
                logger.warning("Answer generation failed: %s", exc)

        # Fallback: concatenate chunk texts
        texts = []
        for c in chunks:
            if isinstance(c, str):
                texts.append(c)
            elif isinstance(c, dict):
                texts.append(c.get("text", str(c)))
            elif hasattr(c, "text"):
                texts.append(str(getattr(c, "text")))
            else:
                texts.append(str(c))

        return " ".join(texts[:5])  # first 5 chunks

    def _get_chunk_id(self, chunk: Any) -> str:
        """Extract chunk ID from various representations."""
        if isinstance(chunk, str):
            return chunk
        if isinstance(chunk, dict):
            for key in ("id", "chunk_id"):
                if key in chunk:
                    return str(chunk[key])
            return str(chunk)
        if hasattr(chunk, "chunk_id"):
            return str(getattr(chunk, "chunk_id"))
        if hasattr(chunk, "id"):
            return str(getattr(chunk, "id"))
        return str(chunk)

    def _get_citation_sources(self, chunks: list[Any]) -> list[str]:
        """Return sources in the same order as the public Citation list."""
        if chunks and all(
            hasattr(chunk, "chunk_id")
            and hasattr(chunk, "score")
            and hasattr(chunk, "text")
            and hasattr(chunk, "metadata")
            for chunk in chunks
        ):
            from src.core.response.citation_generator import CitationGenerator

            return [
                self._normalize_source(citation.source)
                for citation in CitationGenerator().generate(chunks)
                if self._normalize_source(citation.source)
            ]

        sources: list[str] = []
        for chunk in chunks:
            metadata = chunk.get("metadata", chunk) if isinstance(chunk, dict) else {}
            if isinstance(metadata, dict):
                source = metadata.get("source_path", metadata.get("source", ""))
                normalized = self._normalize_source(source)
                if normalized:
                    sources.append(normalized)
        return sources

    @staticmethod
    def _normalize_source(value: Any) -> str:
        from src.libs.evaluator.custom_evaluator import normalize_source_identifier

        return normalize_source_identifier(value)

    @staticmethod
    def _aggregate_metrics(results: list[QueryResult]) -> dict[str, Any]:
        """Compute auditable aggregate metrics across evaluated queries.

        Args:
            results: List of QueryResult with per-query metrics.

        Returns:
            Dictionary of average metric values.
        """
        if not results:
            return {}

        aggregate: dict[str, Any] = {}
        for level_name in ("chunk_level", "source_level"):
            level_metrics: dict[str, Any] = {}
            for metric_name in ("hit_at_1", "hit_at_3", "hit_at_k", "mrr"):
                values = [
                    float(level[metric_name])
                    for result in results
                    if isinstance((level := result.metrics.get(level_name)), dict)
                    and level.get("evaluation_status") == "evaluated"
                    and level.get(metric_name) is not None
                ]
                level_metrics[metric_name] = _aggregate_values(values)
            aggregate[level_name] = level_metrics

        aggregate["citation"] = {
            "presence": _aggregate_values(
                [
                    float(result.metrics["citation_presence"])
                    for result in results
                    if result.metrics.get("citation_presence") is not None
                    and not result.expect_empty_result
                ]
            ),
            "expected_source_match": _aggregate_values(
                [
                    float(result.metrics["citation_expected_source_match"])
                    for result in results
                    if result.metrics.get("citation_expected_source_match")
                    is not None
                ]
            ),
        }
        aggregate["empty_result_handling"] = _aggregate_values(
            [
                float(result.empty_result_handling)
                for result in results
                if result.empty_result_handling is not None
            ]
        )

        legacy_hit_rate = [
            float(result.metrics["hit_rate"])
            for result in results
            if isinstance(result.metrics.get("hit_rate"), (int, float))
        ]
        legacy_mrr = [
            float(result.metrics["mrr"])
            for result in results
            if isinstance(result.metrics.get("mrr"), (int, float))
        ]
        primary = (
            aggregate["chunk_level"]
            if aggregate["chunk_level"]["mrr"]["denominator"]
            else aggregate["source_level"]
        )
        aggregate["hit_rate"] = (
            _aggregate_values(legacy_hit_rate)["rate"]
            if legacy_hit_rate
            else primary["hit_at_k"]["rate"]
        )
        aggregate["mrr"] = (
            _aggregate_values(legacy_mrr)["rate"]
            if legacy_mrr
            else primary["mrr"]["rate"]
        )

        extra_keys = {
            key
            for result in results
            for key, value in result.metrics.items()
            if isinstance(value, (int, float))
            and key not in {"hit_rate", "mrr", "citation_presence"}
        }
        for key in sorted(extra_keys):
            aggregate[key] = _aggregate_values(
                [
                    float(result.metrics[key])
                    for result in results
                    if isinstance(result.metrics.get(key), (int, float))
                ]
            )["rate"]
        return aggregate


def _aggregate_values(values: list[float]) -> dict[str, Any]:
    numerator = sum(values)
    denominator = len(values)
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": numerator / denominator if denominator else None,
    }
