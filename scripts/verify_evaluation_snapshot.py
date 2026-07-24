#!/usr/bin/env python
"""Verify an evaluation snapshot by recomputing its aggregate metrics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.observability.evaluation.snapshot import load_and_verify_snapshot  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", help="Path to the snapshot JSON file")
    args = parser.parse_args()

    try:
        snapshot = load_and_verify_snapshot(args.snapshot)
    except (OSError, ValueError) as exc:
        print(f"Snapshot verification failed: {exc}", file=sys.stderr)
        return 1

    print(
        "Snapshot verified: "
        f"{snapshot['query_count']} queries, "
        f"{snapshot['evaluated_count']} evaluated, "
        f"{snapshot['not_evaluated_count']} not evaluated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
