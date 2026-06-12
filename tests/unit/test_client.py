# SPDX-License-Identifier: Apache-2.0
"""Unit tests for TraCSS and AsyncTraCSS Okta auth logic."""

import base64
import os
import time
from http import HTTPStatus

import httpx
import pytest
import respx

from tracss.client import AsyncTraCSS, TraCSS, _require_env

TOKEN_URL = "https://tracssamu.okta-gov.com/oauth2/aus1358llxDldKxE80j7/v1/token"
FAKE_TOKEN = "test-token-abc"


@respx.mock
def test_token_is_fetched_lazily(respx_mock: respx.MockRouter) -> None:
    """Token must not be fetched at construction time."""
    client = TraCSS(client_id="cid", client_secret="csec")
    assert client._token is None


@respx.mock
def test_token_fetched_on_first_call(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    token = client._get_token()
    assert token == FAKE_TOKEN


@respx.mock
def test_token_uses_http_basic_auth(respx_mock: respx.MockRouter) -> None:
    route = respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    client._get_token()
    request = route.calls[0].request
    expected = "Basic " + base64.b64encode(b"cid:csec").decode()
    assert request.headers["authorization"] == expected


@respx.mock
def test_expired_token_is_refreshed(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": "new-token", "expires_in": 86400}
        )
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    client._token = "old-token"
    client._token_expires_at = time.monotonic() - 1  # already expired
    token = client._get_token()
    assert token == "new-token"


@respx.mock
def test_valid_token_is_reused(respx_mock: respx.MockRouter) -> None:
    route = respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    client._get_token()
    client._get_token()
    assert route.call_count == 1


def test_missing_env_raises() -> None:
    os.environ.pop("TRACSS_CLIENT_ID", None)
    with pytest.raises(KeyError, match="TRACSS_CLIENT_ID"):
        TraCSS()


def test_require_env_raises_on_missing() -> None:
    os.environ.pop("__TRACSS_TEST_VAR__", None)
    with pytest.raises(KeyError, match="__TRACSS_TEST_VAR__"):
        _require_env("__TRACSS_TEST_VAR__")


def test_custom_okta_domain_is_used() -> None:
    client = TraCSS(
        client_id="cid",
        client_secret="csec",
        okta_domain="custom.okta.example.com",
    )
    assert client._okta_domain == "custom.okta.example.com"


def test_default_okta_values() -> None:
    client = TraCSS(client_id="cid", client_secret="csec")
    assert client._okta_domain == "tracssamu.okta-gov.com"
    assert client._okta_auth_server_id == "aus1358llxDldKxE80j7"
    assert client._okta_scope == "tracssusername"


# ── Error path tests ─────────────────────────────────────────────────────────


@respx.mock
def test_okta_401_raises_http_status_error(respx_mock: respx.MockRouter) -> None:
    """Okta 401 must surface as HTTPStatusError, not a JSON/KeyError."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, text="Unauthorized")
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    with pytest.raises(httpx.HTTPStatusError):
        client._get_token()


@respx.mock
def test_okta_missing_access_token_raises_value_error(
    respx_mock: respx.MockRouter,
) -> None:
    """Okta 200 with no access_token must raise ValueError with a clear message."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"token_type": "Bearer"})
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    with pytest.raises(ValueError, match="access_token"):
        client._get_token()


@respx.mock
def test_okta_missing_expires_in_falls_back_to_3600(
    respx_mock: respx.MockRouter,
) -> None:
    """Missing expires_in must not crash — fall back to 3600s."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"access_token": FAKE_TOKEN})
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    token = client._get_token()
    assert token == FAKE_TOKEN
    # expiry should be ~3570s from now (3600 - 30)
    assert client._token_expires_at > 0


@respx.mock
def test_okta_connect_error_propagates(respx_mock: respx.MockRouter) -> None:
    """Network-level error during token fetch must propagate to the caller."""
    respx_mock.post(TOKEN_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    client = TraCSS(client_id="cid", client_secret="csec")
    with pytest.raises(httpx.ConnectError):
        client._get_token()


@respx.mock
def test_bearer_token_sent_on_api_call(respx_mock: respx.MockRouter) -> None:
    """The Authorization: Bearer header must be set on every outbound API request."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    api_route = respx_mock.get("https://api.tracss.gov/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    client.subscriber.topics.list()
    assert api_route.called
    assert api_route.calls[0].request.headers["authorization"] == f"Bearer {FAKE_TOKEN}"


# ── AsyncTraCSS token tests ───────────────────────────────────────────────────


@respx.mock
async def test_async_token_not_fetched_at_construction(
    respx_mock: respx.MockRouter,
) -> None:
    """Token must not be fetched at construction time for AsyncTraCSS."""
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    assert client._token is None


@respx.mock
async def test_async_token_fetched_on_first_call(
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    token = await client._aget_token()
    assert token == FAKE_TOKEN


@respx.mock
async def test_async_valid_token_is_reused(respx_mock: respx.MockRouter) -> None:
    route = respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    await client._aget_token()
    await client._aget_token()
    assert route.call_count == 1


@respx.mock
async def test_async_expired_token_is_refreshed(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json={"access_token": "new-async-token", "expires_in": 86400}
        )
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    client._token = "old-token"
    client._token_expires_at = time.monotonic() - 1
    token = await client._aget_token()
    assert token == "new-async-token"


@respx.mock
async def test_async_okta_401_raises_http_status_error(
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, text="Unauthorized")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    with pytest.raises(httpx.HTTPStatusError):
        await client._aget_token()


@respx.mock
async def test_async_okta_missing_access_token_raises_value_error(
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"token_type": "Bearer"})
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    with pytest.raises(ValueError, match="access_token"):
        await client._aget_token()


@respx.mock
async def test_async_okta_missing_expires_in_falls_back_to_3600(
    respx_mock: respx.MockRouter,
) -> None:
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"access_token": FAKE_TOKEN})
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    token = await client._aget_token()
    assert token == FAKE_TOKEN
    assert client._token_expires_at > 0
