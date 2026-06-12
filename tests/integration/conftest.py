# Copyright © Loft Orbital Solutions Inc.
import json
import os
import threading
from collections.abc import Generator
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
import pytest

from tracss import AsyncTraCSS, TraCSS

_NDJSON_PORT = int(os.environ.get("TRACSS_NDJSON_PORT", "4013"))

_CDM_LINE = json.dumps({"headersOnly": None, "default": None})
_OCM_LINE = json.dumps({"headersOnly": None, "default": None})

_NDJSON_ROUTES: dict[str, str] = {
    "/bulkdata/cdm/v2/stream": _CDM_LINE,
    "/bulkdata/cdm/v1/stream": _CDM_LINE,
    "/bulkdata/ocm/v2/stream": _OCM_LINE,
    "/bulkdata/ocm/v1/stream": _OCM_LINE,
}


class _NdjsonHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path in _NDJSON_ROUTES:
            body = (_NDJSON_ROUTES[path] + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture(scope="session")
def ndjson_server() -> Generator[str, None, None]:
    server = HTTPServer(("localhost", _NDJSON_PORT), _NdjsonHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://localhost:{_NDJSON_PORT}"
    server.shutdown()


def _prism_url(env_var: str, default_port: int) -> str:
    return os.environ.get(env_var, f"http://localhost:{default_port}")


def _skip_if_no_prism(url: str) -> None:
    try:
        httpx.get(url, timeout=1)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
        pytest.skip(f"Prism not reachable at {url}")


def _make_client(base_url: str) -> TraCSS:
    """Create a sync client pointing at Prism with a pre-seeded token."""
    client = TraCSS(client_id="fake", client_secret="fake", base_url=base_url)
    client._token = "integration-token"
    client._token_expires_at = float("inf")
    return client


def _make_async_client(base_url: str) -> AsyncTraCSS:
    """Create an async client pointing at Prism with a pre-seeded token."""
    client = AsyncTraCSS(client_id="fake", client_secret="fake", base_url=base_url)
    client._token = "integration-token"
    client._token_expires_at = float("inf")
    return client


# ── Sync fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def subscriber_client() -> TraCSS:
    url = _prism_url("TRACSS_SUBSCRIBER_URL", 4010)
    _skip_if_no_prism(url)
    return _make_client(url)


@pytest.fixture
def bulkdata_client() -> TraCSS:
    url = _prism_url("TRACSS_BULKDATA_URL", 4011)
    _skip_if_no_prism(url)
    return _make_client(url)


@pytest.fixture
def metadata_client() -> TraCSS:
    url = _prism_url("TRACSS_METADATA_URL", 4012)
    _skip_if_no_prism(url)
    return _make_client(url)


# ── Async fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def async_subscriber_client() -> AsyncTraCSS:
    url = _prism_url("TRACSS_SUBSCRIBER_URL", 4010)
    _skip_if_no_prism(url)
    return _make_async_client(url)


@pytest.fixture
def async_bulkdata_client() -> AsyncTraCSS:
    url = _prism_url("TRACSS_BULKDATA_URL", 4011)
    _skip_if_no_prism(url)
    return _make_async_client(url)


@pytest.fixture
def async_metadata_client() -> AsyncTraCSS:
    url = _prism_url("TRACSS_METADATA_URL", 4012)
    _skip_if_no_prism(url)
    return _make_async_client(url)


@pytest.fixture
def ndjson_client(ndjson_server: str) -> TraCSS:
    return _make_client(ndjson_server)


@pytest.fixture
def async_ndjson_client(ndjson_server: str) -> AsyncTraCSS:
    return _make_async_client(ndjson_server)
