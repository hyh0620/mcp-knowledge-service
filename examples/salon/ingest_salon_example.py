"""Ingest the salon example into the salon_knowledge collection."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "examples" / "salon" / "generated_pdfs"
COLLECTION = "salon_knowledge"


def main() -> int:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "ingest.py"),
        "--path",
        str(SOURCE_PATH),
        "--collection",
        COLLECTION,
        "--force",
    ]
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
