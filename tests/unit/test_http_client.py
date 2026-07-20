from unittest.mock import patch

from src.libs.http_client import create_httpx_client


def test_create_httpx_client_uses_configured_local_address(monkeypatch):
    monkeypatch.setenv("HTTPX_LOCAL_ADDRESS", "0.0.0.0")
    transport = object()
    client = object()

    with (
        patch("httpx.HTTPTransport", return_value=transport) as transport_factory,
        patch("httpx.Client", return_value=client) as client_factory,
    ):
        result = create_httpx_client(timeout=3.0)

    assert result is client
    transport_factory.assert_called_once_with(local_address="0.0.0.0")
    client_factory.assert_called_once_with(timeout=3.0, transport=transport)


def test_create_httpx_client_keeps_default_transport(monkeypatch):
    monkeypatch.delenv("HTTPX_LOCAL_ADDRESS", raising=False)
    client = object()

    with patch("httpx.Client", return_value=client) as client_factory:
        result = create_httpx_client(timeout=3.0)

    assert result is client
    client_factory.assert_called_once_with(timeout=3.0)
