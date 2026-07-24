"""Deterministic chunk- and source-level retrieval evaluation."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import PurePosixPath
from typing import Any

from src.libs.evaluator.base_evaluator import BaseEvaluator


def normalize_source_identifier(value: Any) -> str:
    """Return a public, stable filename for source-level comparison."""
    raw = str(value or "").strip().replace("\\", "/")
    if not raw:
        return ""
    return PurePosixPath(raw).name.casefold()


class CustomEvaluator(BaseEvaluator):
    """Compute deterministic retrieval metrics without judging answer text.

    Ground truth can contain chunk IDs, source identifiers, or both. Missing
    ground truth is represented as ``not_evaluated`` and never as a zero score.
    """

    SUPPORTED_METRICS = {"hit_rate", "mrr"}
    _ID_FIELDS = ("id", "chunk_id", "document_id", "doc_id")
    _SOURCE_FIELDS = ("source_path", "source", "source_id")

    def __init__(
        self,
        settings: Any = None,
        metrics: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self.settings = settings
        self.kwargs = kwargs

        if metrics is None:
            metrics = self._metrics_from_settings(settings)

        normalized = [str(metric).strip().lower() for metric in (metrics or [])]
        if not normalized:
            normalized = ["hit_rate", "mrr"]

        unsupported = [metric for metric in normalized if metric not in self.SUPPORTED_METRICS]
        if unsupported:
            raise ValueError(
                "Unsupported custom metrics: "
                f"{', '.join(unsupported)}. Supported: {', '.join(sorted(self.SUPPORTED_METRICS))}"
            )

        self.metrics = normalized

    def evaluate(
        self,
        query: str,
        retrieved_chunks: list[Any],
        generated_answer: str | None = None,
        ground_truth: Any | None = None,
        trace: Any | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Evaluate chunk IDs and normalized source filenames."""
        self.validate_query(query)
        self.validate_retrieved_chunks(retrieved_chunks, allow_empty=True)

        top_k = kwargs.get("top_k", max(len(retrieved_chunks), 1))
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        expected_chunk_ids, expected_sources = self._extract_ground_truth(ground_truth)
        retrieved_chunk_ids = self._extract_ids(
            retrieved_chunks,
            label="retrieved_chunks",
        )
        citation_sources = kwargs.get("citation_sources")
        if citation_sources is not None:
            if not isinstance(citation_sources, list):
                raise ValueError("citation_sources must be a list")
            returned_sources = self._normalize_sources(citation_sources)
        else:
            returned_sources = self._extract_sources(retrieved_chunks)

        chunk_level = self._evaluate_ranking(
            retrieved_chunk_ids,
            expected_chunk_ids,
            top_k=top_k,
        )
        source_level = self._evaluate_ranking(
            returned_sources,
            expected_sources,
            top_k=top_k,
            deduplicate=True,
        )
        evaluated = (
            chunk_level["evaluation_status"] == "evaluated"
            or source_level["evaluation_status"] == "evaluated"
        )

        result: dict[str, Any] = {
            "evaluation_status": "evaluated" if evaluated else "not_evaluated",
            "chunk_level": chunk_level,
            "source_level": source_level,
            "citation_presence": 1.0 if returned_sources else 0.0,
            "citation_expected_source_match": (
                source_level["hit_at_k"]
                if source_level["evaluation_status"] == "evaluated"
                else None
            ),
            "returned_sources": returned_sources,
        }

        # Preserve the original public metric names for callers that evaluate
        # only one ground-truth level.
        primary = (
            chunk_level
            if chunk_level["evaluation_status"] == "evaluated"
            else source_level
        )
        if primary["evaluation_status"] == "evaluated":
            if "hit_rate" in self.metrics:
                result["hit_rate"] = primary["hit_at_k"]
            if "mrr" in self.metrics:
                result["mrr"] = primary["mrr"]

        return result

    def _metrics_from_settings(self, settings: Any) -> list[str]:
        if settings is None:
            return []
        metrics = getattr(getattr(settings, "evaluation", None), "metrics", None)
        if metrics is None:
            return []
        return [str(metric) for metric in metrics]

    def _extract_ground_truth(self, ground_truth: Any | None) -> tuple[list[str], list[str]]:
        if ground_truth is None:
            return [], []
        if isinstance(ground_truth, str):
            return [ground_truth], []
        if isinstance(ground_truth, list):
            return self._extract_ids(ground_truth, label="ground_truth"), []
        if not isinstance(ground_truth, dict):
            raise ValueError(
                f"Unsupported ground_truth type: {type(ground_truth).__name__}. "
                "Expected str, dict, list, or None."
            )

        chunk_values = ground_truth.get(
            "expected_chunk_ids",
            ground_truth.get("ids", []),
        )
        source_values = ground_truth.get(
            "expected_sources",
            ground_truth.get("sources", []),
        )
        if not isinstance(chunk_values, list):
            raise ValueError("ground_truth expected_chunk_ids/ids must be a list")
        if not isinstance(source_values, list):
            raise ValueError("ground_truth expected_sources/sources must be a list")
        return (
            self._extract_ids(chunk_values, label="ground_truth.expected_chunk_ids"),
            self._normalize_sources(source_values),
        )

    def _extract_ids(self, items: Iterable[Any], label: str) -> list[str]:
        ids: list[str] = []
        for index, item in enumerate(items):
            if isinstance(item, str):
                ids.append(item)
                continue
            if isinstance(item, dict):
                for field in self._ID_FIELDS:
                    if field in item:
                        ids.append(str(item[field]))
                        break
                else:
                    raise ValueError(
                        f"Missing id field in {label}[{index}]. "
                        f"Expected one of {', '.join(self._ID_FIELDS)}"
                    )
                continue
            for field in self._ID_FIELDS:
                if hasattr(item, field):
                    ids.append(str(getattr(item, field)))
                    break
            else:
                raise ValueError(
                    f"Unable to extract id from {label}[{index}] of type "
                    f"{type(item).__name__}"
                )
        return ids

    def _extract_sources(self, items: Iterable[Any]) -> list[str]:
        sources: list[str] = []
        for item in items:
            metadata: dict[str, Any] = {}
            if isinstance(item, dict):
                raw_metadata = item.get("metadata")
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata
                else:
                    metadata = item
            else:
                raw_metadata = getattr(item, "metadata", None)
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata

            source = next(
                (metadata[field] for field in self._SOURCE_FIELDS if metadata.get(field)),
                "",
            )
            normalized = normalize_source_identifier(source)
            if normalized:
                sources.append(normalized)
        return sources

    def _normalize_sources(self, values: Iterable[Any]) -> list[str]:
        normalized = [normalize_source_identifier(value) for value in values]
        return [value for value in normalized if value]

    @staticmethod
    def _evaluate_ranking(
        returned: Sequence[str],
        expected: Sequence[str],
        *,
        top_k: int,
        deduplicate: bool = False,
    ) -> dict[str, Any]:
        expected_set = set(expected)
        if not expected_set:
            return {
                "evaluation_status": "not_evaluated",
                "first_relevant_rank": None,
                "hit_at_1": None,
                "hit_at_3": None,
                "hit_at_k": None,
                "mrr": None,
                "k": top_k,
            }

        ranked = list(returned)
        if deduplicate:
            ranked = list(dict.fromkeys(ranked))

        first_rank = next(
            (rank for rank, value in enumerate(ranked, start=1) if value in expected_set),
            None,
        )
        return {
            "evaluation_status": "evaluated",
            "first_relevant_rank": first_rank,
            "hit_at_1": 1.0 if first_rank == 1 else 0.0,
            "hit_at_3": 1.0 if first_rank is not None and first_rank <= 3 else 0.0,
            "hit_at_k": (
                1.0 if first_rank is not None and first_rank <= top_k else 0.0
            ),
            "mrr": 1.0 / first_rank if first_rank is not None else 0.0,
            "k": top_k,
        }
