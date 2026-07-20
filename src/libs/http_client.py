"""Shared HTTP client construction for external model providers."""

from __future__ import annotations

import os
from typing import Any

import httpx


def create_httpx_client(**kwargs: Any) -> httpx.Client:
    """Create a client with an optional explicit local bind address."""
    local_address = os.getenv("HTTPX_LOCAL_ADDRESS", "").strip()
    if local_address:
        kwargs["transport"] = httpx.HTTPTransport(local_address=local_address)
    return httpx.Client(**kwargs)
