"""Compatibility entry point for MCP Knowledge Service.

Prefer:

    python -m src.mcp_server.server
"""

from __future__ import annotations

import sys

from src.mcp_server.server import run_stdio_server


if __name__ == "__main__":
    raise SystemExit(run_stdio_server())
