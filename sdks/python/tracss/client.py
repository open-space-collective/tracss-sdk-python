# SPDX-License-Identifier: Apache-2.0
"""TraCSS SDK client - transparent Okta client-credentials auth (sync + async)."""

from __future__ import annotations

import asyncio
import os
import threading
import time
from typing import Any, cast

import httpx

from .base_client import AsyncBaseTraCSS, BaseTraCSS


class _OktaTokenMixin:
    """Shared Okta client-credentials state and sync token logic."""

    _DEFAULT_OKTA_DOMAIN: str = "tracssamu.okta-gov.com"
    _DEFAULT_AUTH_SERVER_ID: str = "aus1358llxDldKxE80j7"
    _DEFAULT_SCOPE: str = "tracssusername"

    def _init_okta(
        self,
        client_id: str | None,
        client_secret: str | None,
        okta_domain: str | None,
        okta_auth_server_id: str | None,
        okta_scope: str | None,
    ) -> None:
        self._client_id: str = client_id or _require_env("TRACSS_CLIENT_ID")
        self._client_secret: str = client_secret or _require_env("TRACSS_CLIENT_SECRET")
        self._okta_domain: str = okta_domain or os.environ.get(
            "TRACSS_OKTA_DOMAIN", self._DEFAULT_OKTA_DOMAIN
        )
        self._okta_auth_server_id: str = okta_auth_server_id or os.environ.get(
            "TRACSS_OKTA_AUTH_SERVER_ID", self._DEFAULT_AUTH_SERVER_ID
        )
        self._okta_scope: str = okta_scope or os.environ.get(
            "TRACSS_OKTA_SCOPE", self._DEFAULT_SCOPE
        )
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._lock: threading.Lock = threading.Lock()

    def _token_url(self) -> str:
        return f"https://{self._okta_domain}/oauth2/{self._okta_auth_server_id}/v1/token"

    def _fetch_token(self) -> tuple[str, float]:
        resp = httpx.post(
            self._token_url(),
            data={"grant_type": "client_credentials", "scope": self._okta_scope},
            auth=(self._client_id, self._client_secret),
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
        return payload["access_token"], time.monotonic() + payload["expires_in"] - 30

    def _get_token(self) -> str:
        with self._lock:
            if self._token is None or time.monotonic() >= self._token_expires_at:
                self._token, self._token_expires_at = self._fetch_token()
        return self._token


class TraCSS(_OktaTokenMixin, BaseTraCSS):
    """Sync TraCSS client with automatic Okta client-credentials auth.

    Args:
        client_id (str | None): OAuth client ID. Falls back to TRACSS_CLIENT_ID env var.
        client_secret (str | None): OAuth client secret. Falls back to
            TRACSS_CLIENT_SECRET.
        okta_domain (str | None): Okta domain for token exchange. Falls back to
            TRACSS_OKTA_DOMAIN, then the built-in default.
        okta_auth_server_id (str | None): Okta auth server ID. Falls back to
            TRACSS_OKTA_AUTH_SERVER_ID, then the built-in default.
        okta_scope (str | None): Space-separated OAuth scopes. Falls back to
            TRACSS_OKTA_SCOPE, then the built-in default.
        **kwargs (Any): Forwarded to BaseTraCSS.
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        okta_domain: str | None = None,
        okta_auth_server_id: str | None = None,
        okta_scope: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._init_okta(
            client_id, client_secret, okta_domain, okta_auth_server_id, okta_scope
        )
        BaseTraCSS.__init__(self, token=self._get_token, **kwargs)


class AsyncTraCSS(_OktaTokenMixin, AsyncBaseTraCSS):
    """Async TraCSS client with automatic Okta client-credentials auth.

    Uses httpx.AsyncClient for non-blocking token refresh in async contexts.

    Args:
        client_id (str | None): OAuth client ID. Falls back to TRACSS_CLIENT_ID env var.
        client_secret (str | None): OAuth client secret. Falls back to
            TRACSS_CLIENT_SECRET.
        okta_domain: Okta domain for token exchange. Falls back to
            TRACSS_OKTA_DOMAIN, then the built-in default.
        okta_auth_server_id (str | None): Okta auth server ID. Falls back to
            TRACSS_OKTA_AUTH_SERVER_ID, then the built-in default.
        okta_scope (str | None): Space-separated OAuth scopes. Falls back to
            TRACSS_OKTA_SCOPE, then the built-in default.
        **kwargs (Any): Forwarded to AsyncBaseTraCSS.
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        okta_domain: str | None = None,
        okta_auth_server_id: str | None = None,
        okta_scope: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._init_okta(
            client_id, client_secret, okta_domain, okta_auth_server_id, okta_scope
        )
        self._async_lock: asyncio.Lock = asyncio.Lock()
        AsyncBaseTraCSS.__init__(
            self,
            token=self._get_token,
            async_token=self._aget_token,
            **kwargs,
        )

    async def _afetch_token(self) -> tuple[str, float]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self._token_url(),
                data={"grant_type": "client_credentials", "scope": self._okta_scope},
                auth=(self._client_id, self._client_secret),
                timeout=10,
            )
        resp.raise_for_status()
        payload = resp.json()
        return payload["access_token"], time.monotonic() + payload["expires_in"] - 30

    async def _aget_token(self) -> str:
        async with self._async_lock:
            if self._token is None or time.monotonic() >= self._token_expires_at:
                self._token, self._token_expires_at = await self._afetch_token()
        return cast("str", self._token)


def _require_env(name: str) -> str:
    """Return os.environ[name] or raise a descriptive KeyError."""
    try:
        return os.environ[name]
    except KeyError as exc:
        raise KeyError(
            f"Required environment variable {name!r} is not set. "
            f"Pass it explicitly to TraCSS() or export it in your shell."
        ) from exc
