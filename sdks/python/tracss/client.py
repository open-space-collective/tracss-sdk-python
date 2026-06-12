# SPDX-License-Identifier: Apache-2.0
"""TraCSS SDK client - transparent Okta client-credentials auth (sync + async)."""

from __future__ import annotations

import asyncio
import os
import threading
import time
from http import HTTPStatus
from typing import Any, cast

import httpx

from .base_client import AsyncBaseTraCSS, BaseTraCSS
from .core.api_error import ApiError
from .metadata.cdm.client import AsyncCdmClient, CdmClient
from .metadata.client import AsyncMetadataClient, MetadataClient
from .metadata.ocm.client import AsyncOcmClient, OcmClient
from .metadata.tip_reports.client import AsyncTipReportsClient, TipReportsClient


def _call_or_raw(call, **kwargs):
    """Call a generated list method; return raw str body for non-JSON 200 responses.

    Defaults format to 'json'. If a non-JSON format is explicitly requested
    (e.g. 'KVN', 'xml', 'csv'), the API returns text/plain which the generated
    parser cannot handle — ApiError(status_code=200) is caught here and the raw
    body is returned as a str instead. Non-200 errors are re-raised unchanged.
    """
    kwargs.setdefault("format", "json")
    try:
        return call(**kwargs)
    except ApiError as e:
        if e.status_code == HTTPStatus.OK:
            return e.body
        raise


async def _async_call_or_raw(awaitable):
    """Async mirror of _call_or_raw for coroutine list methods."""
    try:
        return await awaitable
    except ApiError as e:
        if e.status_code == HTTPStatus.OK:
            return e.body
        raise


class _JsonCdmClient(CdmClient):
    """CdmClient that defaults format='json'; returns raw str for non-JSON formats."""

    def list(self, **kwargs):
        return _call_or_raw(super().list, **kwargs)

    def list_by_operational_batch(self, **kwargs):
        return _call_or_raw(super().list_by_operational_batch, **kwargs)

    def list_v1(self, **kwargs):
        return _call_or_raw(super().list_v1, **kwargs)

    def list_by_operational_batch_v1(self, **kwargs):
        return _call_or_raw(super().list_by_operational_batch_v1, **kwargs)


class _AsyncJsonCdmClient(AsyncCdmClient):
    """Async version of _JsonCdmClient."""

    async def list(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list(**kwargs))

    async def list_by_operational_batch(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list_by_operational_batch(**kwargs))

    async def list_v1(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list_v1(**kwargs))

    async def list_by_operational_batch_v1(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list_by_operational_batch_v1(**kwargs))


class _JsonOcmClient(OcmClient):
    """OcmClient that defaults format='json'; returns raw str for non-JSON formats.

    list_by_operational_batch* already return application/json only and are unaffected.
    """

    def list(self, **kwargs):
        return _call_or_raw(super().list, **kwargs)

    def list_v1(self, **kwargs):
        return _call_or_raw(super().list_v1, **kwargs)


class _AsyncJsonOcmClient(AsyncOcmClient):
    """Async version of _JsonOcmClient."""

    async def list(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list(**kwargs))

    async def list_v1(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list_v1(**kwargs))


class _JsonTipReportsClient(TipReportsClient):
    """TipReportsClient that defaults format='json'; returns raw str for non-JSON."""

    def list(self, **kwargs):
        return _call_or_raw(super().list, **kwargs)


class _AsyncJsonTipReportsClient(AsyncTipReportsClient):
    """Async version of _JsonTipReportsClient."""

    async def list(self, **kwargs):
        kwargs.setdefault("format", "json")
        return await _async_call_or_raw(super().list(**kwargs))


class _MetadataWithJsonDefaults(MetadataClient):
    """MetadataClient whose cdm/ocm/tip_reports sub-clients default format to 'json'."""

    @property
    def cdm(self):
        if self._cdm is None:
            self._cdm = _JsonCdmClient(client_wrapper=self._client_wrapper)
        return self._cdm

    @property
    def ocm(self):
        if self._ocm is None:
            self._ocm = _JsonOcmClient(client_wrapper=self._client_wrapper)
        return self._ocm

    @property
    def tip_reports(self):
        if self._tip_reports is None:
            self._tip_reports = _JsonTipReportsClient(client_wrapper=self._client_wrapper)
        return self._tip_reports


class _AsyncMetadataWithJsonDefaults(AsyncMetadataClient):
    """Async version of _MetadataWithJsonDefaults."""

    @property
    def cdm(self):
        if self._cdm is None:
            self._cdm = _AsyncJsonCdmClient(client_wrapper=self._client_wrapper)
        return self._cdm

    @property
    def ocm(self):
        if self._ocm is None:
            self._ocm = _AsyncJsonOcmClient(client_wrapper=self._client_wrapper)
        return self._ocm

    @property
    def tip_reports(self):
        if self._tip_reports is None:
            self._tip_reports = _AsyncJsonTipReportsClient(
                client_wrapper=self._client_wrapper
            )
        return self._tip_reports


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
        token = payload.get("access_token")
        if not token:
            raise ValueError(
                f"Okta token response is missing 'access_token'. "
                f"Keys returned: {sorted(payload)}"
            )
        expires_in = int(payload.get("expires_in") or 3600)
        return token, time.monotonic() + max(expires_in - 30, 0)

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
        base_url (str | None): Override the default API base URL
            (``https://api.tracss.gov``). Useful for pointing at a Prism mock
            server during local testing, e.g. ``base_url="http://localhost:4010"``.
        **kwargs (Any): Forwarded to BaseTraCSS.
    """

    def __init__(  # noqa: PLR0913
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        okta_domain: str | None = None,
        okta_auth_server_id: str | None = None,
        okta_scope: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._init_okta(
            client_id, client_secret, okta_domain, okta_auth_server_id, okta_scope
        )
        BaseTraCSS.__init__(self, token=self._get_token, base_url=base_url, **kwargs)

    @property
    def metadata(self):  # noqa: D102
        if self._metadata is None:
            self._metadata = _MetadataWithJsonDefaults(
                client_wrapper=self._client_wrapper
            )
        return self._metadata


class AsyncTraCSS(_OktaTokenMixin, AsyncBaseTraCSS):
    """Async TraCSS client with automatic Okta client-credentials auth.

    Uses httpx.AsyncClient for non-blocking token refresh in async contexts.

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
        base_url (str | None): Override the default API base URL
            (``https://api.tracss.gov``). Useful for pointing at a Prism mock
            server during local testing, e.g. ``base_url="http://localhost:4010"``.
        **kwargs (Any): Forwarded to AsyncBaseTraCSS.
    """

    def __init__(  # noqa: PLR0913
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        okta_domain: str | None = None,
        okta_auth_server_id: str | None = None,
        okta_scope: str | None = None,
        base_url: str | None = None,
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
            base_url=base_url,
            **kwargs,
        )

    @property
    def metadata(self):  # noqa: D102
        if self._metadata is None:
            self._metadata = _AsyncMetadataWithJsonDefaults(
                client_wrapper=self._client_wrapper
            )
        return self._metadata

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
        token = payload.get("access_token")
        if not token:
            raise ValueError(
                f"Okta token response is missing 'access_token'. "
                f"Keys returned: {sorted(payload)}"
            )
        expires_in = int(payload.get("expires_in") or 3600)
        return token, time.monotonic() + max(expires_in - 30, 0)

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
