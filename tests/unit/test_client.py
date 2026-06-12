# Copyright © Loft Orbital Solutions Inc.
import base64
import os
import time

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
            200, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    token = client._get_token()
    assert token == FAKE_TOKEN


@respx.mock
def test_token_uses_http_basic_auth(respx_mock: respx.MockRouter) -> None:
    route = respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            200, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
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
            200, json={"access_token": "new-token", "expires_in": 86400}
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
            200, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
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
            200, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
        )
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    token = await client._aget_token()
    assert token == FAKE_TOKEN


@respx.mock
async def test_async_valid_token_is_reused(respx_mock: respx.MockRouter) -> None:
    route = respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(
            200, json={"access_token": FAKE_TOKEN, "expires_in": 86400}
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
            200, json={"access_token": "new-async-token", "expires_in": 86400}
        )
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    client._token = "old-token"
    client._token_expires_at = time.monotonic() - 1
    token = await client._aget_token()
    assert token == "new-async-token"
