# SPDX-License-Identifier: Apache-2.0
"""Shared pytest fixtures for all test layers."""

import inspect
import typing

import pytest

from tracss import TraCSS
from tracss.client import AsyncTraCSS


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: requires Prism mock servers")


@pytest.fixture
def api_client() -> TraCSS:
    """Sync client with a pre-seeded token - bypasses Okta for method unit tests."""
    client = TraCSS(client_id="fake", client_secret="fake")
    client._token = "unit-test-token"
    client._token_expires_at = float("inf")
    return client


@pytest.fixture
async def async_api_client() -> AsyncTraCSS:
    """Async client with a pre-seeded token - bypasses Okta for method unit tests."""
    client = AsyncTraCSS(client_id="fake", client_secret="fake")
    client._token = "unit-test-token"
    client._token_expires_at = float("inf")
    return client


@pytest.fixture(params=["sync", "async"], ids=["sync", "async"])
def client_kind(request: pytest.FixtureRequest) -> TraCSS | AsyncTraCSS:
    """Pre-seeded sync or async client for tests whose behavior must be identical.

    Covers both client flavors (pass-through requests, error mapping, response
    parsing). Pair with `maybe_await` so the same test body works for either.

    Only use this for behavior that generated/wrapper code implements once and
    shares between sync and async. Hand-duplicated implementations (Okta token
    fetch, StreamResult/AsyncStreamResult, _call_or_raw/_async_call_or_raw) must
    keep separate explicit sync/async tests instead, since a bug fixed in one
    is not guaranteed fixed in the other.
    """
    if request.param == "sync":
        client: TraCSS | AsyncTraCSS = TraCSS(client_id="fake", client_secret="fake")
    else:
        client = AsyncTraCSS(client_id="fake", client_secret="fake")
    client._token = "unit-test-token"
    client._token_expires_at = float("inf")
    return client


async def maybe_await(value: typing.Any) -> typing.Any:
    """Await `value` if it's awaitable, else return it unchanged.

    Lets one test body drive both client_kind flavors.
    """
    if inspect.isawaitable(value):
        return await value
    return value
