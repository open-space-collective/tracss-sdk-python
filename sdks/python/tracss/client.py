# SPDX-License-Identifier: Apache-2.0
"""TraCSS SDK client with transparent Okta client-credentials auth (sync + async)."""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
import os
import threading
import time
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

import httpx

from .base_client import AsyncBaseTraCSS, BaseTraCSS
from .bulk_data.announcements.client import AnnouncementsClient as BulkAnnouncementsClient
from .bulk_data.announcements.client import (
    AsyncAnnouncementsClient as AsyncBulkAnnouncementsClient,
)
from .bulk_data.cdm.client import AsyncCdmClient as AsyncBulkCdmClient
from .bulk_data.cdm.client import CdmClient as BulkCdmClient
from .bulk_data.client import AsyncBulkDataClient, BulkDataClient
from .bulk_data.ocm.client import AsyncOcmClient as AsyncBulkOcmClient
from .bulk_data.ocm.client import OcmClient as BulkOcmClient
from .bulk_data.tip.client import AsyncTipClient as AsyncBulkTipClient
from .bulk_data.tip.client import TipClient as BulkTipClient
from .core.api_error import ApiError
from .metadata.cdm.client import AsyncCdmClient, CdmClient
from .metadata.cdm.types.list_by_operational_batch_cdm_response import (
    ListByOperationalBatchCdmResponse,
)
from .metadata.cdm.types.list_cdm_response import ListCdmResponse
from .metadata.client import AsyncMetadataClient, MetadataClient
from .metadata.conjunction_events.client import (
    AsyncConjunctionEventsClient,
    ConjunctionEventsClient,
)
from .metadata.conjunction_events.types.list_conjunction_events_response import (
    ListConjunctionEventsResponse,
)
from .metadata.contact_directory.client import (
    AsyncContactDirectoryClient,
    ContactDirectoryClient,
)
from .metadata.ocm.client import AsyncOcmClient, OcmClient
from .metadata.ocm.types.list_ocm_response import ListOcmResponse
from .metadata.space_track.client import AsyncSpaceTrackClient, SpaceTrackClient
from .metadata.tip_reports.client import AsyncTipReportsClient, TipReportsClient
from .metadata.tracss_cat.client import AsyncTracssCatClient, TracssCatClient
from .subscriber.client import AsyncSubscriberClient, SubscriberClient
from .subscriber.messages.client import AsyncMessagesClient, MessagesClient
from .subscriber.messages.types.list_messages_response import ListMessagesResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

    from .bulk_data.cdm.types.stream_cdm_response import StreamCdmResponse
    from .bulk_data.ocm.types.stream_ocm_response import StreamOcmResponse
    from .core.client_wrapper import AsyncClientWrapper

_T = TypeVar("_T")
_F = TypeVar("_F", bound="Callable[..., Any]")
_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())


_OKTA_TOKEN_TIMEOUT: int = 10
_TOKEN_REFRESH_BUFFER_SECS: int = 30
_DEFAULT_TOKEN_TTL_SECS: int = 3600  # fallback when IdP omits expires_in


class RawResponse:
    """Raw CCSDS/text body returned when ``format`` is not ``'json'``.

    Returned by CDM, OCM, and TIP-report list methods when the caller passes an
    explicit ``format="KVN"``, ``format="xml"``, or ``format="csv"`` argument.
    Use ``str(result)`` or ``result.body`` to access the text.  Use
    ``isinstance(result, RawResponse)`` to detect this branch at the call site.

    .. code-block:: python

        result = client.metadata.cdm.list(format="KVN")
        if isinstance(result, RawResponse):
            kvn_text = str(result)
        else:
            records = result.data
    """

    def __init__(self, body: str) -> None:
        self._body = body

    @property
    def body(self) -> str:
        """The raw response body as a string."""
        return self._body

    def __str__(self) -> str:
        return self._body

    def __repr__(self) -> str:
        preview = self._body[:60].replace("\n", "\\n")
        return f"RawResponse({preview!r})"


class StreamResult(Generic[_T]):
    """Iterable wrapper around bulk-data NDJSON streams with zero-record detection.

    All bulk-data ``stream()`` methods return a ``StreamResult`` rather than a
    bare iterator.  Existing iteration code works unchanged:

    .. code-block:: python

        for record in client.bulk_data.cdm.stream(...):
            process(record)

    After full iteration the ``record_count`` attribute reflects how many items
    were consumed.  When the stream is exhausted with zero records a WARNING is
    logged automatically, a signal of possible auth failure, filter
    misconfiguration, or an unexpected data gap.  Callers may additionally
    inspect ``record_count`` directly:

    .. code-block:: python

        result = client.bulk_data.cdm.stream(...)
        records = list(result)
        if result.record_count == 0:
            raise RuntimeError("Expected CDMs but received none. Check filters.")

    The warning fires only when the iterator is *fully exhausted* with zero
    items.  Early termination (``break``) does not trigger it.

    Note:
        ``StreamResult`` is a **single-pass iterator** that returns itself via
        ``__iter__``. Re-iterating after exhaustion yields nothing. To iterate
        the same data twice, collect into a ``list`` first.

    Warning:
        The zero-record warning is logged at ``WARNING`` level.  If your
        pipeline suppresses WARNING logs or does not monitor them, a silent
        auth failure or filter misconfiguration will go undetected.  For
        safety-critical pipelines, check ``record_count`` explicitly after
        full iteration:

        .. code-block:: python

            result = client.bulk_data.cdm.stream(...)
            records = list(result)
            if result.record_count == 0:
                raise RuntimeError("No CDMs returned. Verify auth and filters.")
    """

    def __init__(self, iterator: Iterator[_T], description: str = "") -> None:
        self._iter = iterator
        self._count = 0
        self._description = description
        self._exhausted = False
        self._iterator_errored = False

    def __iter__(self) -> Iterator[_T]:
        return self

    def __next__(self) -> _T:
        try:
            item = next(self._iter)
            self._count += 1
        except StopIteration:
            if not self._exhausted:
                self._exhausted = True
                if self._count == 0:
                    _log.warning(
                        "Bulk-data stream returned 0 records %s. "
                        "Verify filters, credentials, and data availability.",
                        f"[{self._description}]" if self._description else "",
                    )
            raise
        except Exception:
            self._iterator_errored = True
            raise
        else:
            return item

    @property
    def record_count(self) -> int:
        """Number of records consumed so far, or total count after full iteration."""
        return self._count

    @property
    def iteration_errored(self) -> bool:
        """True if a mid-stream exception escaped the iterator.

        Does NOT detect per-line drops.

        Per-line parse failures (``JSONDecodeError``, ``ValidationError``) are
        swallowed by the generated NDJSON iterator's ``except Exception: pass``
        handler and will NOT set this flag.  The stream silently appears shorter.
        Use ``record_count`` as the reliable guard for safety-critical pipelines.

        Distinguishes a mid-stream network or auth error from a naturally empty
        stream.  Check this after catching an exception from iteration:

        .. code-block:: python

            result = client.bulk_data.cdm.stream(...)
            try:
                records = list(result)
            except Exception:
                if result.iteration_errored:
                    raise RuntimeError("Stream failed mid-flight. Partial data only.")
                raise

        Warning:
            **``iteration_errored`` only fires when an exception escapes the
            underlying iterator.**

            The generated NDJSON iterator wraps each line in
            ``except Exception: pass`` so that non-data lines embedded in the
            stream (keep-alives, status envelopes) don't crash the whole
            iteration.  A genuine ``JSONDecodeError`` or ``ValidationError`` on
            a real data record is caught by the same handler and silently
            dropped, the stream just appears shorter.  Because the exception
            never escapes the generator, ``iteration_errored`` stays ``False``
            and there is no error signal.

            For safety-critical SSA pipelines, do not rely on ``iteration_errored``
            alone.  Compare ``record_count`` against an expected minimum:

            .. code-block:: python

                result = client.bulk_data.cdm.stream(...)
                records = list(result)
                if result.record_count < expected_minimum:
                    raise RuntimeError(
                        f"Expected >= {expected_minimum} CDMs, got {result.record_count}."
                        " Possible silent record drop. Check filters and schema version."
                    )

            A fix has been filed upstream with the Fern generator to change
            ``except Exception: pass`` to a logged warning so drops surface in
            the SDK's log output.  Until that lands, ``record_count`` is the
            only reliable guard.
        """
        return self._iterator_errored


# Async counterpart of StreamResult. Intentionally not unified; Python's sync
# and async iterator protocols (__next__ vs __anext__, Iterator vs AsyncIterator)
# are incompatible base classes.
class AsyncStreamResult(Generic[_T]):
    """Async iterable wrapper around bulk-data NDJSON streams with zero-record detection.

    Async counterpart of ``StreamResult``.  All async bulk-data ``stream()``
    methods return an ``AsyncStreamResult``.  Existing iteration code works
    unchanged:

    .. code-block:: python

        async for record in client.bulk_data.cdm.stream(...):
            process(record)

    After full iteration the ``record_count`` attribute reflects how many items
    were consumed.  When the stream is exhausted with zero records a WARNING is
    logged automatically.
    """

    def __init__(self, iterator: AsyncIterator[_T], description: str = "") -> None:
        self._iter = iterator
        self._count = 0
        self._description = description
        self._exhausted = False
        self._iterator_errored = False

    def __aiter__(self) -> AsyncIterator[_T]:
        return self

    async def __anext__(self) -> _T:
        try:
            item = await self._iter.__anext__()
            self._count += 1
        except StopAsyncIteration:
            if not self._exhausted:
                self._exhausted = True
                if self._count == 0:
                    _log.warning(
                        "Bulk-data stream returned 0 records %s."
                        " Verify filters, credentials, and data availability.",
                        f"[{self._description}]" if self._description else "",
                    )
            raise
        except Exception:
            self._iterator_errored = True
            raise
        else:
            return item

    @property
    def record_count(self) -> int:
        """Number of records consumed so far, or total count after full iteration."""
        return self._count

    @property
    def iteration_errored(self) -> bool:
        """True if a mid-stream exception escaped the iterator.

        Does NOT detect per-line drops.

        Per-line parse failures are swallowed by the generated NDJSON iterator
        and will NOT set this flag.  See ``StreamResult.iteration_errored`` for
        the full explanation and the recommended ``record_count`` guard.
        """
        return self._iterator_errored


def _require_env(name: str) -> str:
    """Return os.environ[name] or raise a descriptive ValueError.

    Treats empty string as unset. An empty credential would produce a cryptic
    Okta 401 rather than a clear error at construction time.
    """
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f"Required environment variable {name!r} is not set or is empty. "
            f"Pass it explicitly to TraCSS() or export it in your shell."
        )
    return value


def _parse_token_response(payload: dict[str, Any], url: str) -> tuple[str, float]:
    """Validate an Okta token JSON payload and return (token, monotonic_expiry).

    _fetch_token and _afetch_token share identical validation and expiry arithmetic.
    This is a simple fix for edge cases like expires_in=0.
    """
    token: str | None = payload.get("access_token")
    if not token:
        raise ValueError(
            f"Okta token response is missing 'access_token'. "
            f"Keys returned: {sorted(payload)}"
        )
    try:
        raw_expires_in: Any = payload.get("expires_in")
        expires_in: int = (
            int(raw_expires_in) if raw_expires_in is not None else _DEFAULT_TOKEN_TTL_SECS
        )
    except (ValueError, TypeError):
        _log.warning(
            "Okta expires_in=%r is not an integer; using default", raw_expires_in
        )
        expires_in = _DEFAULT_TOKEN_TTL_SECS
    effective_ttl: int = max(expires_in - _TOKEN_REFRESH_BUFFER_SECS, 0)
    if effective_ttl == 0:
        _log.warning(
            "Okta token expires_in=%d <= %ds refresh buffer; "
            "token will refresh on every request",
            expires_in,
            _TOKEN_REFRESH_BUFFER_SECS,
        )
    _log.debug("Token acquired (url=%s, expires_in=%ds)", url, expires_in)
    return token, time.monotonic() + effective_ttl


def _inject_json_accept(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Return kwargs with Accept: application/json injected when format is json.

    The Fern-generated client sends no Accept header by default (httpx uses */*).
    The TraCSS API uses content negotiation and returns KVN (text/plain) when no
    explicit Accept preference is set. Injecting ``Accept: application/json`` ensures
    the server returns JSON even when ``format='json'`` is set only via query parameter.

    Skips injection if the caller already set an Accept header.
    Returns a new dict; does not mutate the input.
    """
    ro: dict[str, Any] = dict(kwargs.get("request_options") or {})
    extra: dict[str, str] = dict(ro.get("additional_headers") or {})
    if not any(k.lower() == "accept" for k in extra):
        extra["Accept"] = "application/json"
    ro["additional_headers"] = extra
    return {**kwargs, "request_options": ro}


def _call_or_raw(call: Callable[..., _T], **kwargs: Any) -> _T | RawResponse:
    """Call a generated list method; return RawResponse for non-JSON 200 responses.

    Defaults format to 'json' and injects ``Accept: application/json`` so the
    TraCSS API returns JSON regardless of its default content-negotiation preference
    (KVN when ``Accept: */*``). For non-JSON formats, the server returns text/plain
    which the generated parser cannot handle. ``ApiError(status_code=200)`` is
    caught here and the raw body is returned as a ``RawResponse``. Non-200 errors
    are re-raised unchanged.

    Returns ``_T`` when ``format='json'`` (default). Returns ``RawResponse`` (raw
    CCSDS text) for any other ``format=`` value; use ``isinstance(result, RawResponse)``
    to detect this branch.
    """
    kwargs.setdefault("format", "json")
    if kwargs["format"] == "json":
        kwargs = _inject_json_accept(kwargs)
    try:
        return call(**kwargs)
    except ApiError as e:
        if e.status_code == HTTPStatus.OK and isinstance(e.body, str):
            return RawResponse(e.body)
        raise


async def _async_call_or_raw(
    call: Callable[..., Awaitable[_T]], **kwargs: Any
) -> _T | RawResponse:
    """Async mirror of _call_or_raw. See its docstring for the Accept header rationale.

    Takes the unbound method and **kwargs (not a pre-created coroutine) so that
    both ``format='json'`` and ``Accept: application/json`` are injected centrally.
    Callers must not call ``kwargs.setdefault`` themselves.

    Returns ``_T`` when ``format='json'`` (default). Returns ``RawResponse`` (raw
    CCSDS text) for any other ``format=`` value; use ``isinstance(result, RawResponse)``
    to detect this branch.
    """
    kwargs.setdefault("format", "json")
    if kwargs["format"] == "json":
        kwargs = _inject_json_accept(kwargs)
    try:
        return await call(**kwargs)
    except ApiError as e:
        if e.status_code == HTTPStatus.OK and isinstance(e.body, str):
            return RawResponse(e.body)
        raise


def _empty_on_204(
    factory: Callable[[], _T], call: Callable[[], _T | RawResponse]
) -> _T | RawResponse:
    """Return ``factory()`` when the API answers 204 No Content (empty result set).

    Orthogonal to _call_or_raw: this concerns only the empty-result convention, not
    content negotiation. The empty-result sentinel is **per-controller**, not a
    single server-wide status (live-confirmed 2026-07-12): cdm, ocm, space_track
    (+ nested), and conjunction_events answer **204** with an empty body, which the
    generated parser turns into ``ApiError(status_code=204)`` (it calls ``.json()``
    on the empty body). This substitutes an empty typed result so an ordinary "no
    matches" query does not surface as an exception. The concrete empty type is
    supplied by the caller, which owns its return type.

    Endpoints that answer 404 with a text sentinel instead (tracss_cat,
    contact_directory) use the sibling ``_empty_on_not_found``. Endpoints that
    already return ``200 []`` (translation_errors, metadata.announcements) or
    ``None`` on empty (tip_reports) never reach either helper and need no wrapper.
    """
    try:
        return call()
    except ApiError as e:
        if e.status_code == HTTPStatus.NO_CONTENT:
            return factory()
        raise


async def _async_empty_on_204(
    factory: Callable[[], _T], call: Callable[[], Awaitable[_T | RawResponse]]
) -> _T | RawResponse:
    """Async mirror of _empty_on_204. See its docstring for the rationale."""
    try:
        return await call()
    except ApiError as e:
        if e.status_code == HTTPStatus.NO_CONTENT:
            return factory()
        raise


def _empty_on_not_found(
    factory: Callable[[], _T], call: Callable[[], _T | RawResponse], *, message: str
) -> _T | RawResponse:
    """Return ``factory()`` when the API signals an empty result via 404 + sentinel text.

    Sibling of ``_empty_on_204`` for the controllers that answer 404 instead of 204
    on an empty result (live-confirmed 2026-07-12): ``tracss_cat`` ->
    "No TracssCat(s) found.", ``contact_directory`` -> "No contacts found". The
    ``message`` substring guard is required so a genuine 404 (bad route, missing
    resource) still raises rather than being masked as an empty result.

    Fragility: this couples correctness to the server's English 404 wording. If
    TraCSS rewords, localizes, or JSON-ifies the body, an empty query would start
    raising ``NotFoundError`` again. Prism mock tests cannot catch that, so this is
    guarded by the live smoke tests in ``tests/smoke/`` (which assert an
    impossible-filter query returns empty rather than raising). Update the sentinel
    here and the smoke expectation together if the server message changes.
    """
    try:
        return call()
    except ApiError as e:
        if (
            e.status_code == HTTPStatus.NOT_FOUND
            and isinstance(e.body, str)
            and message in e.body
        ):
            return factory()
        raise


async def _async_empty_on_not_found(
    factory: Callable[[], _T],
    call: Callable[[], Awaitable[_T | RawResponse]],
    *,
    message: str,
) -> _T | RawResponse:
    """Async mirror of _empty_on_not_found. See its docstring for the rationale."""
    try:
        return await call()
    except ApiError as e:
        if (
            e.status_code == HTTPStatus.NOT_FOUND
            and isinstance(e.body, str)
            and message in e.body
        ):
            return factory()
        raise


def _wrap_generated(
    generated: Callable[..., Any], return_annotation: str
) -> Callable[[_F], _F]:
    """Copy a generated method's parameter signature onto a ``**kwargs`` wrapper.

    The JSON/stream wrappers below take ``**kwargs`` so behavior tweaks can be added
    without restating each generated method's (often dozens of) parameters. That
    erases the signature that ``help()``, ``inspect.signature``, Jupyter, and
    runtime-introspecting IDEs would otherwise show. ``functools.wraps`` restores it
    by pointing ``__wrapped__`` at the generated method, then this overrides the
    return annotation (wrappers widen it, e.g. to add ``RawResponse``) and keeps any
    docstring already written on the wrapper.

    Note: this restores the *runtime* signature only. Static type checkers
    (mypy/pyright) still see ``**kwargs`` and will not flag a misspelled parameter;
    the ``with_raw_response`` clients retain fully-typed signatures for that.
    """

    def deco(fn: _F) -> _F:
        own_doc = fn.__doc__
        functools.wraps(generated)(fn)
        if own_doc:
            fn.__doc__ = own_doc
        # functools.wraps points __wrapped__ at the generated method, so
        # inspect.signature() would otherwise report the generated (narrower)
        # return type. Set an explicit __signature__ (which takes precedence over
        # __wrapped__) so help()/IDEs show the wrapper's widened return type.
        fn.__signature__ = inspect.signature(generated).replace(  # type: ignore[attr-defined]
            return_annotation=return_annotation
        )
        fn.__annotations__ = {**generated.__annotations__, "return": return_annotation}
        return fn

    return deco


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
        resolved_id = (
            client_id if client_id is not None else _require_env("TRACSS_CLIENT_ID")
        )
        resolved_secret = (
            client_secret
            if client_secret is not None
            else _require_env("TRACSS_CLIENT_SECRET")
        )
        if not resolved_id:
            raise ValueError(
                "client_id must not be empty. "
                "Pass it explicitly to TraCSS() or export TRACSS_CLIENT_ID."
            )
        if not resolved_secret:
            raise ValueError(
                "client_secret must not be empty. "
                "Pass it explicitly to TraCSS() or export TRACSS_CLIENT_SECRET."
            )
        # Reject explicit empty-string overrides - omit the kwarg or use env vars.
        if okta_domain is not None and not okta_domain:
            raise ValueError(
                "okta_domain must not be empty. "
                "Omit it or export TRACSS_OKTA_DOMAIN to use the built-in default."
            )
        if okta_domain and "://" in okta_domain:
            raise ValueError(
                "okta_domain must not include a URL scheme (e.g. 'https://'). "
                "Pass only the hostname, e.g. 'tracssamu.okta-gov.com'."
            )
        if okta_auth_server_id is not None and not okta_auth_server_id:
            raise ValueError(
                "okta_auth_server_id must not be empty. "
                "Omit it or export TRACSS_OKTA_AUTH_SERVER_ID."
            )
        if okta_scope is not None:
            if not okta_scope.strip():
                raise ValueError(
                    "okta_scope must not be empty or whitespace. "
                    "Omit it or export TRACSS_OKTA_SCOPE to use the built-in default."
                )
            okta_scope = okta_scope.strip()
        self._client_id: str = resolved_id
        self._client_secret: str = resolved_secret
        self._okta_domain: str = (
            okta_domain
            or (os.environ.get("TRACSS_OKTA_DOMAIN") or "").strip()
            or self._DEFAULT_OKTA_DOMAIN
        ).rstrip("/")
        self._okta_auth_server_id: str = (
            okta_auth_server_id
            or (os.environ.get("TRACSS_OKTA_AUTH_SERVER_ID") or "").strip()
            or self._DEFAULT_AUTH_SERVER_ID
        )
        self._okta_scope: str = (
            okta_scope
            or (os.environ.get("TRACSS_OKTA_SCOPE") or "").strip()
            or self._DEFAULT_SCOPE
        )
        self._token: str | None = None
        self._token_expires_at: float = time.monotonic() - 1  # start expired

    def _token_url(self) -> str:
        return f"https://{self._okta_domain}/oauth2/{self._okta_auth_server_id}/v1/token"

    def _fetch_token(self) -> tuple[str, float]:
        url = self._token_url()
        _log.debug("Fetching Okta token (url=%s)", url)
        try:
            resp = httpx.post(
                url,
                data={"grant_type": "client_credentials", "scope": self._okta_scope},
                auth=(self._client_id, self._client_secret),
                timeout=_OKTA_TOKEN_TIMEOUT,
            )
            resp.raise_for_status()
        except Exception:
            _log.error("Okta token request failed (url=%s)", url)
            raise
        try:
            payload = resp.json()
        except Exception as exc:
            _log.error("Okta token endpoint returned non-JSON (url=%s)", url)
            # Body logged at DEBUG only. May contain sensitive IdP context.
            _log.debug("Okta non-JSON response body: %r", resp.content[:300])
            raise ValueError(
                f"Okta token endpoint returned non-JSON (url={url!r}); "
                "enable DEBUG logging for the response body"
            ) from exc
        return _parse_token_response(payload, url)


class _StreamingCdmBulkClient(BulkCdmClient):
    """CdmClient (bulk_data) that wraps stream results in StreamResult."""

    @_wrap_generated(BulkCdmClient.stream, "StreamResult[StreamCdmResponse]")
    def stream(self, **kwargs: Any) -> StreamResult[StreamCdmResponse]:
        return StreamResult(super().stream(**kwargs), "bulk_data.cdm.stream")


class _AsyncStreamingCdmBulkClient(AsyncBulkCdmClient):
    """AsyncCdmClient (bulk_data) that wraps stream results in AsyncStreamResult."""

    @_wrap_generated(AsyncBulkCdmClient.stream, "AsyncStreamResult[StreamCdmResponse]")
    def stream(self, **kwargs: Any) -> AsyncStreamResult[StreamCdmResponse]:
        # super().stream() is an async generator function; calling it returns
        # the async generator object synchronously. No await needed here.
        return AsyncStreamResult(super().stream(**kwargs), "bulk_data.cdm.stream")


class _StreamingOcmBulkClient(BulkOcmClient):
    """OcmClient (bulk_data) that wraps stream results in StreamResult."""

    @_wrap_generated(BulkOcmClient.stream, "StreamResult[StreamOcmResponse]")
    def stream(self, **kwargs: Any) -> StreamResult[StreamOcmResponse]:
        return StreamResult(super().stream(**kwargs), "bulk_data.ocm.stream")


class _AsyncStreamingOcmBulkClient(AsyncBulkOcmClient):
    """AsyncOcmClient (bulk_data) that wraps stream results in AsyncStreamResult."""

    @_wrap_generated(AsyncBulkOcmClient.stream, "AsyncStreamResult[StreamOcmResponse]")
    def stream(self, **kwargs: Any) -> AsyncStreamResult[StreamOcmResponse]:
        return AsyncStreamResult(super().stream(**kwargs), "bulk_data.ocm.stream")


class _StreamingTipBulkClient(BulkTipClient):
    """TipClient (bulk_data) that wraps stream results in StreamResult."""

    @_wrap_generated(BulkTipClient.stream, "StreamResult[Any]")
    def stream(self, **kwargs: Any) -> StreamResult[Any]:
        return StreamResult(super().stream(**kwargs), "bulk_data.tip.stream")


class _AsyncStreamingTipBulkClient(AsyncBulkTipClient):
    """AsyncTipClient (bulk_data) that wraps stream results in AsyncStreamResult."""

    @_wrap_generated(AsyncBulkTipClient.stream, "AsyncStreamResult[Any]")
    def stream(self, **kwargs: Any) -> AsyncStreamResult[Any]:
        return AsyncStreamResult(super().stream(**kwargs), "bulk_data.tip.stream")


class _BulkDataWithStreamResult(BulkDataClient):
    """BulkDataClient whose CDM/OCM/TIP sub-clients return StreamResult wrappers.

    Unlike the metadata list wrappers, the bulk streams do NOT force
    ``format='json'``/``Accept: application/json``. The bulk stream endpoints
    return ``application/x-ndjson`` under the default ``Accept`` (live-confirmed
    2026-07-12), so no content-negotiation override is needed; these wrappers only
    add zero-record detection via ``StreamResult``. See
    ``tests/smoke/test_smoke.py::test_bulkdata_cdm_stream`` for the regression guard.
    """

    @property
    def cdm(self) -> _StreamingCdmBulkClient:
        if self._cdm is None:
            self._cdm = _StreamingCdmBulkClient(client_wrapper=self._client_wrapper)
        return cast("_StreamingCdmBulkClient", self._cdm)

    @property
    def ocm(self) -> _StreamingOcmBulkClient:
        if self._ocm is None:
            self._ocm = _StreamingOcmBulkClient(client_wrapper=self._client_wrapper)
        return cast("_StreamingOcmBulkClient", self._ocm)

    @property
    def tip(self) -> _StreamingTipBulkClient:
        if self._tip is None:
            self._tip = _StreamingTipBulkClient(client_wrapper=self._client_wrapper)
        return cast("_StreamingTipBulkClient", self._tip)

    @property
    def announcements(self) -> BulkAnnouncementsClient:
        if self._announcements is None:
            self._announcements = BulkAnnouncementsClient(
                client_wrapper=self._client_wrapper
            )
        return cast("BulkAnnouncementsClient", self._announcements)


class _AsyncBulkDataWithStreamResult(AsyncBulkDataClient):
    """AsyncBulkDataClient whose CDM/OCM/TIP sub-clients return AsyncStreamResult.

    No lock: asyncio is single-threaded and cooperative.  Sync properties contain
    no ``await`` points, so no task switch can interleave between the ``is None``
    check and the assignment.
    """

    @property
    def cdm(self) -> _AsyncStreamingCdmBulkClient:
        if self._cdm is None:
            self._cdm = _AsyncStreamingCdmBulkClient(client_wrapper=self._client_wrapper)
        return cast("_AsyncStreamingCdmBulkClient", self._cdm)

    @property
    def ocm(self) -> _AsyncStreamingOcmBulkClient:
        if self._ocm is None:
            self._ocm = _AsyncStreamingOcmBulkClient(client_wrapper=self._client_wrapper)
        return cast("_AsyncStreamingOcmBulkClient", self._ocm)

    @property
    def tip(self) -> _AsyncStreamingTipBulkClient:
        if self._tip is None:
            self._tip = _AsyncStreamingTipBulkClient(client_wrapper=self._client_wrapper)
        return cast("_AsyncStreamingTipBulkClient", self._tip)

    @property
    def announcements(self) -> AsyncBulkAnnouncementsClient:
        if self._announcements is None:
            self._announcements = AsyncBulkAnnouncementsClient(
                client_wrapper=self._client_wrapper
            )
        return cast("AsyncBulkAnnouncementsClient", self._announcements)


class _JsonCdmClient(CdmClient):
    """CdmClient that defaults format='json' on list calls.

    Without this wrapper the TraCSS Metadata API returns CCSDS KVN
    (``text/plain``) by default, which the Fern-generated response parser
    cannot handle. It always calls ``.json()`` and raises
    ``ApiError(status_code=200, body=<KVN text>)`` for non-JSON content.

    Supported ``format=`` values: ``"json"`` (SDK default, returns typed
    response), ``"KVN"``, ``"xml"``, ``"csv"`` (returns raw ``str``).
    Use ``isinstance(result, RawResponse)`` to distinguish raw-text responses.

    ``# type: ignore[override]`` on each method is intentional: widening the
    return type to include ``RawResponse`` is an LSP violation, but composition
    over inheritance is rejected here because forwarding the full ``CdmClient``
    surface is more fragile against API drift than concentrated suppressions.
    ``test_codegen_contract.py`` tests guard against unintended surface changes.
    """

    @_wrap_generated(CdmClient.list, "ListCdmResponse | RawResponse")
    def list(self, **kwargs: Any) -> ListCdmResponse | RawResponse:  # type: ignore[override]
        bound = super().list
        return _empty_on_204(ListCdmResponse, lambda: _call_or_raw(bound, **kwargs))

    @_wrap_generated(
        CdmClient.list_by_operational_batch,
        "ListByOperationalBatchCdmResponse | RawResponse",
    )
    def list_by_operational_batch(  # type: ignore[override]
        self, **kwargs: Any
    ) -> ListByOperationalBatchCdmResponse | RawResponse:
        bound = super().list_by_operational_batch
        return _empty_on_204(
            ListByOperationalBatchCdmResponse,
            lambda: _call_or_raw(bound, **kwargs),
        )


class _AsyncJsonCdmClient(AsyncCdmClient):
    """Async version of _JsonCdmClient."""

    @_wrap_generated(AsyncCdmClient.list, "ListCdmResponse | RawResponse")
    async def list(self, **kwargs: Any) -> ListCdmResponse | RawResponse:  # type: ignore[override]
        bound = super().list
        return await _async_empty_on_204(
            ListCdmResponse, lambda: _async_call_or_raw(bound, **kwargs)
        )

    @_wrap_generated(
        AsyncCdmClient.list_by_operational_batch,
        "ListByOperationalBatchCdmResponse | RawResponse",
    )
    async def list_by_operational_batch(  # type: ignore[override]
        self, **kwargs: Any
    ) -> ListByOperationalBatchCdmResponse | RawResponse:
        bound = super().list_by_operational_batch
        return await _async_empty_on_204(
            ListByOperationalBatchCdmResponse,
            lambda: _async_call_or_raw(bound, **kwargs),
        )


class _JsonOcmClient(OcmClient):
    """OcmClient that defaults ``format='json'`` and handles edge-case API responses.

    - list: defaults ``format='json'``; returns ``RawResponse`` for non-JSON formats;
      returns an empty ``ListOcmResponse`` on HTTP 204 (empty result set).
    - list_by_operational_batch: catches HTTP 204 No Content (empty result set) and
      returns ``[]`` instead of raising ``ApiError``. The API returns 204 when no batches
      match the query.

    Both list endpoints answer 204 with an empty body when no records match (a
    server-wide convention, live-confirmed); ``_empty_on_204`` keeps that from
    surfacing as an ``ApiError``.

    ``# type: ignore[override]`` on each method is intentional. Same rationale
    as ``_JsonCdmClient``.
    """

    @_wrap_generated(OcmClient.list, "ListOcmResponse | RawResponse")
    def list(self, **kwargs: Any) -> ListOcmResponse | RawResponse:  # type: ignore[override]
        bound = super().list
        return _empty_on_204(ListOcmResponse, lambda: _call_or_raw(bound, **kwargs))

    @_wrap_generated(OcmClient.list_by_operational_batch, "list[Any]")
    def list_by_operational_batch(self, **kwargs: Any) -> list[Any]:  # type: ignore[override, valid-type]
        try:
            return super().list_by_operational_batch(**kwargs)
        except ApiError as exc:
            if exc.status_code == HTTPStatus.NO_CONTENT:
                return []
            raise

    @_wrap_generated(OcmClient.upload, "dict[str, Any] | str")
    def upload(self, **kwargs: Any) -> dict[str, Any] | str:  # type: ignore[override]
        """Upload OCM; injects Accept: application/json.

        Returns a dict on JSON 2xx, or raw text if the server responds with
        text/plain on 2xx (the spec allows both for 201 Created).
        Check ``isinstance(result, str)`` to detect the text/plain path.
        """
        kwargs = _inject_json_accept(kwargs)
        try:
            return super().upload(**kwargs)
        except ApiError as exc:
            sc = exc.status_code
            if (
                sc is not None
                and HTTPStatus.OK <= sc < HTTPStatus.MULTIPLE_CHOICES
                and isinstance(exc.body, str)
            ):
                return exc.body
            raise


class _AsyncJsonOcmClient(AsyncOcmClient):
    """Async version of _JsonOcmClient."""

    @_wrap_generated(AsyncOcmClient.list, "ListOcmResponse | RawResponse")
    async def list(self, **kwargs: Any) -> ListOcmResponse | RawResponse:  # type: ignore[override]
        bound = super().list
        return await _async_empty_on_204(
            ListOcmResponse, lambda: _async_call_or_raw(bound, **kwargs)
        )

    @_wrap_generated(AsyncOcmClient.list_by_operational_batch, "list[Any]")
    async def list_by_operational_batch(self, **kwargs: Any) -> list[Any]:  # type: ignore[override, valid-type]
        try:
            return await super().list_by_operational_batch(**kwargs)
        except ApiError as exc:
            if exc.status_code == HTTPStatus.NO_CONTENT:
                return []
            raise

    @_wrap_generated(AsyncOcmClient.upload, "dict[str, Any] | str")
    async def upload(self, **kwargs: Any) -> dict[str, Any] | str:  # type: ignore[override]
        """Async version of _JsonOcmClient.upload()."""
        kwargs = _inject_json_accept(kwargs)
        try:
            return await super().upload(**kwargs)
        except ApiError as exc:
            sc = exc.status_code
            if (
                sc is not None
                and HTTPStatus.OK <= sc < HTTPStatus.MULTIPLE_CHOICES
                and isinstance(exc.body, str)
            ):
                return exc.body
            raise


class _JsonTipReportsClient(TipReportsClient):
    """TipReportsClient defaulting ``format='json'``; raw ``str`` for non-JSON formats."""

    # The generated TipReportsClient.list() returns typing.Any (no concrete response
    # type exists in the generated output). RawResponse is included to document the
    # override intent, not to narrow the type. Any | RawResponse is still Any to
    # mypy, but communicates that callers may receive a RawResponse for non-JSON formats.
    @_wrap_generated(TipReportsClient.list, "Any | RawResponse")
    def list(self, **kwargs: Any) -> Any | RawResponse:
        return _call_or_raw(super().list, **kwargs)


class _AsyncJsonTipReportsClient(AsyncTipReportsClient):
    """Async version of _JsonTipReportsClient."""

    # See _JsonTipReportsClient.list for why the return type is Any | RawResponse.
    @_wrap_generated(AsyncTipReportsClient.list, "Any | RawResponse")
    async def list(self, **kwargs: Any) -> Any | RawResponse:
        return await _async_call_or_raw(super().list, **kwargs)


class _JsonMessagesClient(MessagesClient):
    """MessagesClient that returns an empty response for HTTP 204 (no messages)."""

    @_wrap_generated(MessagesClient.list, "ListMessagesResponse")
    def list(self, **kwargs: Any) -> ListMessagesResponse:  # type: ignore[override]
        """Return messages; all fields are ``None`` (not ``[]``) on HTTP 204.

        Always guard before iterating: ``if result.cdm_v2:``.
        """
        try:
            return super().list(**kwargs)
        except ApiError as exc:
            if exc.status_code == HTTPStatus.NO_CONTENT:
                return ListMessagesResponse()
            raise


class _AsyncJsonMessagesClient(AsyncMessagesClient):
    """Async version of _JsonMessagesClient."""

    @_wrap_generated(AsyncMessagesClient.list, "ListMessagesResponse")
    async def list(self, **kwargs: Any) -> ListMessagesResponse:  # type: ignore[override]
        try:
            return await super().list(**kwargs)
        except ApiError as exc:
            if exc.status_code == HTTPStatus.NO_CONTENT:
                return ListMessagesResponse()
            raise


class _SubscriberWithMessages(SubscriberClient):
    """SubscriberClient whose messages sub-client handles HTTP 204 (no messages)."""

    @property
    def messages(self) -> _JsonMessagesClient:
        if self._messages is None:
            self._messages = _JsonMessagesClient(client_wrapper=self._client_wrapper)
        return cast("_JsonMessagesClient", self._messages)


class _AsyncSubscriberWithMessages(AsyncSubscriberClient):
    """Async version of _SubscriberWithMessages.

    No lock: asyncio is single-threaded and cooperative; sync properties have
    no ``await`` points, so no task switch can interleave.
    """

    @property
    def messages(self) -> _AsyncJsonMessagesClient:
        if self._messages is None:
            self._messages = _AsyncJsonMessagesClient(client_wrapper=self._client_wrapper)
        return cast("_AsyncJsonMessagesClient", self._messages)


class _EmptySafeSpaceTrackClient(SpaceTrackClient):
    """SpaceTrackClient returning ``[]`` on the 204 empty-result sentinel."""

    @_wrap_generated(SpaceTrackClient.list, "list[SpaceTrack]")
    def list(self, **kwargs: Any) -> Any:
        bound = super().list
        return _empty_on_204(list, lambda: bound(**kwargs))

    @_wrap_generated(SpaceTrackClient.list_nested, "list[SpaceTrackNestedDto]")
    def list_nested(self, **kwargs: Any) -> Any:
        bound = super().list_nested
        return _empty_on_204(list, lambda: bound(**kwargs))


class _AsyncEmptySafeSpaceTrackClient(AsyncSpaceTrackClient):
    """Async version of _EmptySafeSpaceTrackClient."""

    @_wrap_generated(AsyncSpaceTrackClient.list, "list[SpaceTrack]")
    async def list(self, **kwargs: Any) -> Any:
        bound = super().list
        return await _async_empty_on_204(list, lambda: bound(**kwargs))

    @_wrap_generated(AsyncSpaceTrackClient.list_nested, "list[SpaceTrackNestedDto]")
    async def list_nested(self, **kwargs: Any) -> Any:
        bound = super().list_nested
        return await _async_empty_on_204(list, lambda: bound(**kwargs))


def _empty_conjunction_events() -> ListConjunctionEventsResponse:
    """Empty ConjunctionEvents response whose list fields are ``[]``, not ``None``.

    On a 204 the generated model would otherwise default every field to ``None``,
    so ``result.default`` would be ``None`` and iterating it raises ``TypeError``.
    Populating the list fields with ``[]`` keeps an empty result uniformly iterable
    (matching the bare-``[]`` space_track / tracss_cat / contact_directory endpoints).
    """
    return ListConjunctionEventsResponse(default=[], headers_only=[])


class _EmptySafeConjunctionEventsClient(ConjunctionEventsClient):
    """ConjunctionEventsClient returning an empty (iterable) response on 204."""

    @_wrap_generated(ConjunctionEventsClient.list, "ListConjunctionEventsResponse")
    def list(self, **kwargs: Any) -> Any:
        bound = super().list
        return _empty_on_204(_empty_conjunction_events, lambda: bound(**kwargs))


class _AsyncEmptySafeConjunctionEventsClient(AsyncConjunctionEventsClient):
    """Async version of _EmptySafeConjunctionEventsClient."""

    @_wrap_generated(AsyncConjunctionEventsClient.list, "ListConjunctionEventsResponse")
    async def list(self, **kwargs: Any) -> Any:
        bound = super().list
        return await _async_empty_on_204(
            _empty_conjunction_events, lambda: bound(**kwargs)
        )


class _EmptySafeTracssCatClient(TracssCatClient):
    """TracssCatClient returning ``[]`` on the 404 "No TracssCat(s) found." sentinel."""

    @_wrap_generated(TracssCatClient.list, "list[dict[str, Any]]")
    def list(self, **kwargs: Any) -> Any:
        bound = super().list
        return _empty_on_not_found(
            list, lambda: bound(**kwargs), message="No TracssCat(s) found"
        )


class _AsyncEmptySafeTracssCatClient(AsyncTracssCatClient):
    """Async version of _EmptySafeTracssCatClient."""

    @_wrap_generated(AsyncTracssCatClient.list, "list[dict[str, Any]]")
    async def list(self, **kwargs: Any) -> Any:
        bound = super().list
        return await _async_empty_on_not_found(
            list, lambda: bound(**kwargs), message="No TracssCat(s) found"
        )


class _EmptySafeContactDirectoryClient(ContactDirectoryClient):
    """ContactDirectoryClient returning ``[]`` on the 404 "No contacts found" sentinel."""

    @_wrap_generated(
        ContactDirectoryClient.list_operational, "list[OperationalContactInfoDto]"
    )
    def list_operational(self, **kwargs: Any) -> Any:
        bound = super().list_operational
        return _empty_on_not_found(
            list, lambda: bound(**kwargs), message="No contacts found"
        )


class _AsyncEmptySafeContactDirectoryClient(AsyncContactDirectoryClient):
    """Async version of _EmptySafeContactDirectoryClient."""

    @_wrap_generated(
        AsyncContactDirectoryClient.list_operational, "list[OperationalContactInfoDto]"
    )
    async def list_operational(self, **kwargs: Any) -> Any:
        bound = super().list_operational
        return await _async_empty_on_not_found(
            list, lambda: bound(**kwargs), message="No contacts found"
        )


class _MetadataWithJsonDefaults(MetadataClient):
    """MetadataClient with JSON-defaulting and empty-safe list sub-clients.

    Beyond the JSON-defaulting cdm/ocm/tip_reports wrappers, space_track,
    conjunction_events, tracss_cat, and contact_directory are wrapped so their list
    calls return an empty result instead of raising on the API's per-controller
    empty-result sentinel (204 or 404 "No ... found"). See ``_empty_on_204`` /
    ``_empty_on_not_found``.
    """

    @property
    def cdm(self) -> _JsonCdmClient:
        if self._cdm is None:
            self._cdm = _JsonCdmClient(client_wrapper=self._client_wrapper)
        return cast("_JsonCdmClient", self._cdm)  # parent declares CdmClient | None

    @property
    def ocm(self) -> _JsonOcmClient:
        if self._ocm is None:
            self._ocm = _JsonOcmClient(client_wrapper=self._client_wrapper)
        return cast("_JsonOcmClient", self._ocm)  # parent declares OcmClient | None

    @property
    def tip_reports(self) -> _JsonTipReportsClient:
        if self._tip_reports is None:
            self._tip_reports = _JsonTipReportsClient(client_wrapper=self._client_wrapper)
        # cast: parent declares TipReportsClient | None
        return cast("_JsonTipReportsClient", self._tip_reports)

    @property
    def space_track(self) -> _EmptySafeSpaceTrackClient:
        if self._space_track is None:
            self._space_track = _EmptySafeSpaceTrackClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_EmptySafeSpaceTrackClient", self._space_track)

    @property
    def conjunction_events(self) -> _EmptySafeConjunctionEventsClient:
        if self._conjunction_events is None:
            self._conjunction_events = _EmptySafeConjunctionEventsClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_EmptySafeConjunctionEventsClient", self._conjunction_events)

    @property
    def tracss_cat(self) -> _EmptySafeTracssCatClient:
        if self._tracss_cat is None:
            self._tracss_cat = _EmptySafeTracssCatClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_EmptySafeTracssCatClient", self._tracss_cat)

    @property
    def contact_directory(self) -> _EmptySafeContactDirectoryClient:
        if self._contact_directory is None:
            self._contact_directory = _EmptySafeContactDirectoryClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_EmptySafeContactDirectoryClient", self._contact_directory)


class _AsyncMetadataWithJsonDefaults(AsyncMetadataClient):
    """Async version of _MetadataWithJsonDefaults.

    No lock: asyncio is single-threaded and cooperative.  Sync properties contain
    no ``await`` points, so no task switch can interleave between the ``is None``
    check and the assignment.
    """

    def __init__(self, *, client_wrapper: AsyncClientWrapper) -> None:
        super().__init__(client_wrapper=client_wrapper)

    @property
    def cdm(self) -> _AsyncJsonCdmClient:
        if self._cdm is None:
            self._cdm = _AsyncJsonCdmClient(client_wrapper=self._client_wrapper)
        return cast("_AsyncJsonCdmClient", self._cdm)  # parent declares CdmClient | None

    @property
    def ocm(self) -> _AsyncJsonOcmClient:
        if self._ocm is None:
            self._ocm = _AsyncJsonOcmClient(client_wrapper=self._client_wrapper)
        return cast("_AsyncJsonOcmClient", self._ocm)  # parent declares OcmClient | None

    @property
    def tip_reports(self) -> _AsyncJsonTipReportsClient:
        if self._tip_reports is None:
            self._tip_reports = _AsyncJsonTipReportsClient(
                client_wrapper=self._client_wrapper
            )
        # cast: parent declares TipReportsClient | None
        return cast("_AsyncJsonTipReportsClient", self._tip_reports)

    @property
    def space_track(self) -> _AsyncEmptySafeSpaceTrackClient:
        if self._space_track is None:
            self._space_track = _AsyncEmptySafeSpaceTrackClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_AsyncEmptySafeSpaceTrackClient", self._space_track)

    @property
    def conjunction_events(self) -> _AsyncEmptySafeConjunctionEventsClient:
        if self._conjunction_events is None:
            self._conjunction_events = _AsyncEmptySafeConjunctionEventsClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_AsyncEmptySafeConjunctionEventsClient", self._conjunction_events)

    @property
    def tracss_cat(self) -> _AsyncEmptySafeTracssCatClient:
        if self._tracss_cat is None:
            self._tracss_cat = _AsyncEmptySafeTracssCatClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_AsyncEmptySafeTracssCatClient", self._tracss_cat)

    @property
    def contact_directory(self) -> _AsyncEmptySafeContactDirectoryClient:
        if self._contact_directory is None:
            self._contact_directory = _AsyncEmptySafeContactDirectoryClient(
                client_wrapper=self._client_wrapper
            )
        return cast("_AsyncEmptySafeContactDirectoryClient", self._contact_directory)


class TraCSS(_OktaTokenMixin, BaseTraCSS):
    """Sync TraCSS client with automatic Okta client-credentials auth.

    Args:
        client_id (str | None, optional): OAuth client ID. Defaults to the
            TRACSS_CLIENT_ID env var.
        client_secret (str | None, optional): OAuth client secret. Defaults to
            the TRACSS_CLIENT_SECRET env var.
        okta_domain (str | None, optional): Okta domain for token exchange.
            Defaults to TRACSS_OKTA_DOMAIN, then the built-in default.
        okta_auth_server_id (str | None, optional): Okta auth server ID. Defaults
            to TRACSS_OKTA_AUTH_SERVER_ID, then the built-in default.
        okta_scope (str | None, optional): Space-separated OAuth scopes. Defaults
            to TRACSS_OKTA_SCOPE, then the built-in default.
        base_url (str | None, optional): Override the default API base URL
            (``https://api.tracss.gov``). Useful for pointing at a Prism mock
            server during local testing, e.g. ``base_url="http://localhost:4010"``.
        **kwargs (Any): Forwarded to BaseTraCSS.

    Note:
        This client does not retry failed token fetches or API calls. For
        automated pipelines, wrap calls with a retry library such as
        ``tenacity``::

            from tenacity import retry, stop_after_attempt, wait_exponential

            @retry(stop=stop_after_attempt(3), wait=wait_exponential())
            def fetch_cdms():
                return list(client.bulk_data.cdm.stream(...))
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
        # Guards token refresh only (shared self._token / self._token_expires_at).
        # Sub-client caching is a benign first-access race, so it is lock-free -
        # matching the async client and Fern's own generated lazy properties.
        self._lock: threading.Lock = threading.Lock()
        # Callable: Fern invokes it per-request so tokens refresh transparently.
        BaseTraCSS.__init__(self, token=self._get_token, base_url=base_url, **kwargs)

    def _get_token(self) -> str:
        if self._token is None or time.monotonic() >= self._token_expires_at:
            with self._lock:
                if self._token is None or time.monotonic() >= self._token_expires_at:
                    self._token, self._token_expires_at = self._fetch_token()
        return cast("str", self._token)

    @property
    def bulk_data(self) -> _BulkDataWithStreamResult:
        """Return the Bulk Data sub-client with StreamResult-wrapped stream methods.

        This property overrides the Fern-generated one to install
        ``_BulkDataWithStreamResult``, which wraps CDM, OCM, and TIP stream
        iterators so that zero-record streams emit a WARNING automatically.
        """
        if self._bulk_data is None:
            self._bulk_data = _BulkDataWithStreamResult(
                client_wrapper=self._client_wrapper
            )
        return cast("_BulkDataWithStreamResult", self._bulk_data)

    @property
    def subscriber(self) -> _SubscriberWithMessages:
        """Return the Subscriber sub-client with 204-safe messages handling.

        This property overrides the Fern-generated one to install
        ``_SubscriberWithMessages``, whose ``messages.list()`` returns an empty
        ``ListMessagesResponse`` instead of raising ``ApiError`` when the server
        responds with HTTP 204 (no messages available).
        """
        if self._subscriber is None:
            self._subscriber = _SubscriberWithMessages(
                client_wrapper=self._client_wrapper
            )
        return cast("_SubscriberWithMessages", self._subscriber)

    @property
    def metadata(self) -> _MetadataWithJsonDefaults:
        """Return the Metadata sub-client with JSON-defaulting CDM/OCM/TIP wrappers.

        This property overrides the Fern-generated one to install
        ``_MetadataWithJsonDefaults``, which injects ``format='json'`` on list
        calls. The metadata CDM, OCM, and TIP-report list endpoints return CCSDS
        KVN (text/plain) by default; Fern's parser always calls ``.json()``,
        raising ``ApiError(status_code=200)`` for any non-JSON body. The other
        metadata endpoints are JSON-only, and ``bulk_data`` has no multi-format
        issue, so neither needs this override.
        """
        if self._metadata is None:
            self._metadata = _MetadataWithJsonDefaults(
                client_wrapper=self._client_wrapper
            )
        # cast: parent declares _metadata as MetadataClient | None
        return cast("_MetadataWithJsonDefaults", self._metadata)


class AsyncTraCSS(_OktaTokenMixin, AsyncBaseTraCSS):
    """Async TraCSS client with automatic Okta client-credentials auth.

    Uses httpx.AsyncClient for non-blocking token refresh in async contexts.

    Args:
        client_id (str | None, optional): OAuth client ID. Defaults to the
            TRACSS_CLIENT_ID env var.
        client_secret (str | None, optional): OAuth client secret. Defaults to
            the TRACSS_CLIENT_SECRET env var.
        okta_domain (str | None, optional): Okta domain for token exchange.
            Defaults to TRACSS_OKTA_DOMAIN, then the built-in default.
        okta_auth_server_id (str | None, optional): Okta auth server ID. Defaults
            to TRACSS_OKTA_AUTH_SERVER_ID, then the built-in default.
        okta_scope (str | None, optional): Space-separated OAuth scopes. Defaults
            to TRACSS_OKTA_SCOPE, then the built-in default.
        base_url (str | None, optional): Override the default API base URL
            (``https://api.tracss.gov``). Useful for pointing at a Prism mock
            server during local testing, e.g. ``base_url="http://localhost:4010"``.
        **kwargs (Any): Forwarded to AsyncBaseTraCSS.

    Note:
        This client does not retry failed token fetches or API calls. For
        automated pipelines, wrap calls with a retry library such as
        ``tenacity``. For async coroutines use ``AsyncRetrying``; the
        synchronous ``@retry`` decorator does not drive async generators::

            from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

            async def fetch_cdms():
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3), wait=wait_exponential()
                ):
                    with attempt:
                        result = [r async for r in client.bulk_data.cdm.stream(...)]
                return result
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
            # Fern's AsyncClientWrapper.async_get_headers() calls get_headers() (sync)
            # before awaiting async_token(). Passing self._get_token here would block
            # the event loop via httpx.post() whenever the token expires.
            # _sync_token_noop prevents any blocking I/O on the sync path; the async
            # path (async_token=self._aget_token) overwrites the Authorization header
            # unconditionally. See test_async_bearer_header_contains_token* for guards.
            token=self._sync_token_noop,
            async_token=self._aget_token,
            base_url=base_url,
            **kwargs,
        )

    def _sync_token_noop(self) -> str:
        """Placeholder for the sync ``token=`` parameter passed to AsyncBaseTraCSS.

        Fern's ``AsyncClientWrapper.async_get_headers()`` calls ``get_headers()``
        (sync) before awaiting ``async_token()``.  This method prevents any
        blocking I/O on that sync path.  The real token is always set by
        ``async_token=self._aget_token``, which unconditionally overwrites the
        Authorization header afterwards.
        """
        return ""

    def _get_token(self) -> str:
        """Sync token access is not supported on AsyncTraCSS.

        AsyncTraCSS uses ``_aget_token`` (async) for token refresh.  The
        ``_sync_token_noop`` placeholder passed to AsyncBaseTraCSS ensures the
        sync header-building path never performs blocking I/O.  Any direct call
        to ``_get_token`` on an AsyncTraCSS instance is a programming error.
        """
        raise RuntimeError(
            "AsyncTraCSS does not support sync token access. "
            "Use AsyncTraCSS only from async contexts; "
            "call `await client._aget_token()` if you need the token directly."
        )

    @property
    def bulk_data(self) -> _AsyncBulkDataWithStreamResult:
        """Return the async Bulk Data sub-client with AsyncStreamResult wrappers.

        No lock: asyncio is single-threaded and cooperative; sync properties
        have no ``await`` points, so no task switch can interleave.
        """
        if self._bulk_data is None:
            self._bulk_data = _AsyncBulkDataWithStreamResult(
                client_wrapper=self._client_wrapper
            )
        return cast("_AsyncBulkDataWithStreamResult", self._bulk_data)

    @property
    def subscriber(self) -> _AsyncSubscriberWithMessages:
        """Return the async Subscriber sub-client with 204-safe messages handling.

        No lock: asyncio is single-threaded and cooperative; sync properties
        have no ``await`` points, so no task switch can interleave.
        """
        if self._subscriber is None:
            self._subscriber = _AsyncSubscriberWithMessages(
                client_wrapper=self._client_wrapper
            )
        return cast("_AsyncSubscriberWithMessages", self._subscriber)

    @property
    def metadata(self) -> _AsyncMetadataWithJsonDefaults:
        """Return the async Metadata sub-client with JSON-defaulting wrappers.

        This property overrides the Fern-generated one to install
        ``_AsyncMetadataWithJsonDefaults``, which injects ``format='json'`` on
        list calls. The metadata CDM, OCM, and TIP-report list endpoints return
        CCSDS KVN (text/plain) by default; Fern's parser always calls ``.json()``,
        raising ``ApiError(status_code=200)`` for any non-JSON body. The other
        metadata endpoints are JSON-only, and ``bulk_data`` has no multi-format
        issue, so neither needs this override.

        No lock: asyncio is single-threaded and cooperative; sync properties
        have no ``await`` points, so no task switch can interleave.
        """
        if self._metadata is None:
            self._metadata = _AsyncMetadataWithJsonDefaults(
                client_wrapper=self._client_wrapper
            )
        # cast: parent declares _metadata as AsyncMetadataClient | None
        return cast("_AsyncMetadataWithJsonDefaults", self._metadata)

    async def _afetch_token(self) -> tuple[str, float]:
        url = self._token_url()
        _log.debug("Fetching Okta token async (url=%s)", url)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    data={
                        "grant_type": "client_credentials",
                        "scope": self._okta_scope,
                    },
                    auth=(self._client_id, self._client_secret),
                    timeout=_OKTA_TOKEN_TIMEOUT,
                )
                resp.raise_for_status()
        except Exception:
            _log.error("Okta async token request failed (url=%s)", url)
            raise
        # resp.json() is safe outside the async context: httpx buffers the full
        # response body before raise_for_status(), so the data is in memory.
        try:
            payload = resp.json()
        except Exception as exc:
            _log.error("Okta token endpoint returned non-JSON (url=%s)", url)
            # Body logged at DEBUG only - may contain sensitive IdP context.
            _log.debug("Okta non-JSON response body: %r", resp.content[:300])
            raise ValueError(
                f"Okta token endpoint returned non-JSON (url={url!r}); "
                "enable DEBUG logging for the response body"
            ) from exc
        return _parse_token_response(payload, url)

    async def _aget_token(self) -> str:
        async with self._async_lock:
            if self._token is None or time.monotonic() >= self._token_expires_at:
                self._token, self._token_expires_at = await self._afetch_token()
        return cast("str", self._token)
