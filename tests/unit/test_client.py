# SPDX-License-Identifier: Apache-2.0
"""Unit tests for hand-written logic in tracss.client.

Scope: only the free functions/classes hand-written in tracss/client.py -
RawResponse, StreamResult/AsyncStreamResult, _require_env,
_parse_token_response, _inject_json_accept, _call_or_raw/_async_call_or_raw,
_OktaTokenMixin validation, TraCSS/AsyncTraCSS token-fetch orchestration,
sub-client lazy-init/locking, and bearer-header wiring.

Full per-endpoint format/204/error-mapping behavior is covered in
test_metadata.py / test_bulkdata.py / test_subscriber.py - not duplicated here.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import threading
import time
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import httpx
import pytest
import respx

from tracss.client import (
    AsyncStreamResult,
    AsyncTraCSS,
    RawResponse,
    StreamResult,
    TraCSS,
    _async_call_or_raw,
    _call_or_raw,
    _inject_json_accept,
    _OktaTokenMixin,
    _parse_token_response,
    _require_env,
)
from tracss.core.api_error import ApiError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

TOKEN_URL = "https://tracssamu.okta-gov.com/oauth2/aus1358llxDldKxE80j7/v1/token"
FAKE_TOKEN = "test-token-abc"


def _token_response(
    access_token: str = FAKE_TOKEN, expires_in: int = 86400
) -> httpx.Response:
    return httpx.Response(
        HTTPStatus.OK, json={"access_token": access_token, "expires_in": expires_in}
    )


# ---------------------------------------------------------------------------
# RawResponse
# ---------------------------------------------------------------------------


def test_raw_response_str_returns_full_body_unmodified() -> None:
    """str(RawResponse) returns the exact body, independent of .body."""
    body = "CCSDS_CDM_VERS = 1.0\nCREATION_DATE = 2024-001T12:00:00.000"

    result = str(RawResponse(body))

    assert result == body


def test_raw_response_body_property_returns_full_body_unmodified() -> None:
    """.body returns the exact body, independent of str()."""
    body = "CCSDS_CDM_VERS = 1.0"
    r = RawResponse(body)

    result = r.body

    assert result == body


def test_raw_response_empty_body_handled() -> None:
    """An empty string body round-trips through str() and .body without error."""
    r = RawResponse("")

    assert r.body == ""
    assert str(r) == ""
    assert repr(r) == "RawResponse('')"


def test_raw_response_repr_short_body_not_truncated() -> None:
    """A body <=60 chars appears in full in repr(), with no ellipsis."""
    body = "short body"
    r = RawResponse(body)

    result = repr(r)

    assert result == f"RawResponse({body!r})"


def test_raw_response_repr_truncates_body_over_60_chars() -> None:
    """A body >60 chars is truncated to the first 60 chars in repr()."""
    body = "A" * 80
    r = RawResponse(body)

    result = repr(r)

    preview = result[len("RawResponse(") : -1].strip("'")
    assert preview == "A" * 60


def test_raw_response_repr_escapes_embedded_newlines() -> None:
    r"""Newlines in the preview are rendered as the literal two-character '\n'."""
    r = RawResponse("line1\nline2")

    result = repr(r)

    assert "\\n" in result
    assert "\nline2" not in result  # raw newline must not appear inside repr


def test_raw_response_repr_truncation_does_not_mutate_stored_body() -> None:
    """Calling repr() must not change what .body / str() return afterwards."""
    body = "B" * 80 + "\ntail"
    r = RawResponse(body)

    repr(r)

    assert r.body == body
    assert str(r) == body


# ---------------------------------------------------------------------------
# StreamResult (sync)
# ---------------------------------------------------------------------------


def test_stream_result_full_exhaustion_counts_all_records() -> None:
    """record_count equals the number of items after full iteration."""
    result = StreamResult(iter(range(5)))

    consumed = list(result)

    assert consumed == [0, 1, 2, 3, 4]
    assert result.record_count == 5


def test_stream_result_mid_iteration_count_reflects_items_consumed_so_far() -> None:
    """record_count reflects only items pulled so far, before exhaustion."""
    result = StreamResult(iter(range(5)))

    next(result)
    next(result)

    assert result.record_count == 2


def test_stream_result_zero_record_warning_fires_exactly_once_on_exhaustion(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Exhausting an empty stream logs exactly one WARNING mentioning 0 records."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result: StreamResult[Any] = StreamResult(iter([]), "bulk_data.cdm.stream")
        list(result)

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "0 records" in warnings[0].message


def test_stream_result_no_warning_on_nonempty_stream_exhaustion(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Exhausting a stream with >=1 item logs no WARNING."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = StreamResult(iter(["a", "b"]))
        list(result)

    assert not any(r.levelno == logging.WARNING for r in caplog.records)


def test_stream_result_no_warning_when_breaking_before_any_item_consumed(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Breaking before pulling any item must not trigger the zero-record warning.

    Uses the iterator protocol directly (not a `for` loop, which always calls
    __next__ once before the loop body can `break`) so that __next__ is never
    invoked at all. StopIteration is never raised in this path, so _exhausted
    is never set and the warning branch (which only runs on StopIteration)
    cannot fire.
    """
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = StreamResult(iter([1, 2, 3]))
        iter(result)  # __iter__ only - no __next__ call

    assert result.record_count == 0
    assert not any(r.levelno == logging.WARNING for r in caplog.records)


def test_stream_result_no_warning_when_breaking_after_one_item_consumed(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Breaking after consuming >=1 item must not trigger the zero-record warning."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = StreamResult(iter([1, 2, 3]))
        for _ in result:
            break  # consumes exactly one item before breaking

    assert result.record_count == 1
    assert not any(r.levelno == logging.WARNING for r in caplog.records)


def test_stream_result_reiterating_exhausted_stream_yields_nothing() -> None:
    """Iterating an already-exhausted StreamResult a second time yields no items."""
    result = StreamResult(iter([1, 2]))
    list(result)

    second_pass = list(result)

    assert second_pass == []


def test_stream_result_reiterating_exhausted_empty_stream_does_not_double_log(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Re-exhausting an already-warned empty stream logs only one WARNING total."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result: StreamResult[Any] = StreamResult(iter([]))
        list(result)
        list(result)

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1


def test_stream_result_iteration_errored_true_when_exception_escapes() -> None:
    """iteration_errored becomes True only once an exception actually escapes."""

    def bad_iter() -> Iterator[int]:
        yield 1
        raise RuntimeError("network error")

    result = StreamResult(bad_iter())

    with pytest.raises(RuntimeError):
        list(result)

    assert result.iteration_errored


def test_stream_result_iteration_errored_false_on_clean_exhaustion() -> None:
    """iteration_errored stays False when the stream ends via plain StopIteration."""
    result = StreamResult(iter([1, 2]))

    list(result)

    assert not result.iteration_errored


def test_stream_result_original_exception_propagates_unchanged() -> None:
    """The exact exception type and message raised inside the iterator survive.

    __next__ must not wrap or replace the exception - callers rely on
    inspecting the original type/message.
    """

    def bad_iter() -> Iterator[int]:
        yield 1
        raise ValueError("distinctive marker message")

    result = StreamResult(bad_iter())
    next(result)

    with pytest.raises(ValueError, match="distinctive marker message") as exc_info:
        next(result)

    assert type(exc_info.value) is ValueError


def test_stream_result_silent_per_line_drop_not_detectable_via_iteration_errored() -> (
    None
):
    """Per-line drops swallowed inside a generator are invisible to iteration_errored.

    Pins a documented safety-mechanism limitation: the generated NDJSON
    iterator wraps each line in ``except Exception: pass``, so a genuine
    parse failure on a real record never escapes as an exception here.
    iteration_errored stays False and record_count is simply lower than
    expected - record_count is the only reliable guard, per the docstring.
    """

    def iter_with_silent_drop() -> Iterator[str]:
        for item in ["record-1", "malformed", "record-2", "record-3"]:
            try:
                if item == "malformed":
                    raise ValueError("simulated parse failure")  # noqa: TRY301
                yield item
            except ValueError:
                pass  # mirrors: except Exception: pass in the generated _iter()

    result = StreamResult(iter_with_silent_drop())

    records = list(result)

    assert records == ["record-1", "record-2", "record-3"]
    assert result.record_count == 3  # 4 attempted, 1 silently dropped
    assert not result.iteration_errored  # drop is invisible to StreamResult


# ---------------------------------------------------------------------------
# AsyncStreamResult (async mirror of StreamResult - kept separate per policy:
# hand-duplicated implementations, a bug fixed in one isn't guaranteed fixed
# in the other)
# ---------------------------------------------------------------------------


async def _aiter(items: list[Any]) -> AsyncIterator[Any]:
    for item in items:
        yield item


async def test_async_stream_result_full_exhaustion_counts_all_records() -> None:
    """record_count equals the number of items after full async iteration."""
    result = AsyncStreamResult(_aiter([0, 1, 2, 3, 4]))

    consumed = [item async for item in result]

    assert consumed == [0, 1, 2, 3, 4]
    assert result.record_count == 5


async def test_async_stream_result_mid_iteration_count_reflects_items_so_far() -> None:
    """record_count reflects only items pulled so far, before exhaustion."""
    result = AsyncStreamResult(_aiter([0, 1, 2, 3, 4]))

    await result.__anext__()
    await result.__anext__()

    assert result.record_count == 2


async def test_async_stream_result_zero_record_warning_fires_exactly_once(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Exhausting an empty async stream logs exactly one WARNING mentioning 0 records."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = AsyncStreamResult(_aiter([]), "bulk_data.cdm.stream")
        async for _ in result:
            pass

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "0 records" in warnings[0].message


async def test_async_stream_result_no_warning_on_nonempty_stream_exhaustion(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Exhausting an async stream with >=1 item logs no WARNING."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = AsyncStreamResult(_aiter(["record"]))
        async for _ in result:
            pass

    assert not any(r.levelno == logging.WARNING for r in caplog.records)


async def test_async_stream_result_no_warning_when_breaking_before_any_item(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Breaking before pulling any item must not trigger the zero-record warning.

    Uses the async iterator protocol directly (not `async for`, which always
    calls __anext__ once before the loop body can `break`) so __anext__ is
    never invoked at all.
    """
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = AsyncStreamResult(_aiter([1, 2, 3]))
        result.__aiter__()  # __aiter__ only - no __anext__ call

    assert result.record_count == 0
    assert not any(r.levelno == logging.WARNING for r in caplog.records)


async def test_async_stream_result_no_warning_when_breaking_after_one_item(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Breaking after consuming >=1 item must not trigger the zero-record warning."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = AsyncStreamResult(_aiter([1, 2, 3]))
        async for _ in result:
            break

    assert result.record_count == 1
    assert not any(r.levelno == logging.WARNING for r in caplog.records)


async def test_async_stream_result_reiterating_exhausted_stream_yields_nothing() -> None:
    """Iterating an already-exhausted AsyncStreamResult a second time yields nothing."""
    result = AsyncStreamResult(_aiter([1, 2]))
    async for _ in result:
        pass

    second_pass = [item async for item in result]

    assert second_pass == []


async def test_async_stream_result_reiterating_exhausted_empty_does_not_double_log(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Re-exhausting an already-warned empty async stream logs only one WARNING total."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        result = AsyncStreamResult(_aiter([]))
        async for _ in result:
            pass
        async for _ in result:
            pass

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1


async def test_async_stream_result_iteration_errored_true_when_exception_escapes() -> (
    None
):
    """iteration_errored becomes True only once an exception actually escapes."""

    async def bad_aiter() -> AsyncIterator[int]:
        yield 1
        raise RuntimeError("async network error")

    result = AsyncStreamResult(bad_aiter())

    with pytest.raises(RuntimeError):
        async for _ in result:
            pass

    assert result.iteration_errored


async def test_async_stream_result_iteration_errored_false_on_clean_exhaustion() -> None:
    """iteration_errored stays False when the stream ends via plain StopAsyncIteration."""
    result = AsyncStreamResult(_aiter([1, 2]))

    async for _ in result:
        pass

    assert not result.iteration_errored


async def test_async_stream_result_original_exception_propagates_unchanged() -> None:
    """The exact exception type/message raised inside the iterator survive __anext__."""

    async def bad_aiter() -> AsyncIterator[int]:
        yield 1
        raise ValueError("distinctive async marker message")

    result = AsyncStreamResult(bad_aiter())
    await result.__anext__()

    with pytest.raises(ValueError, match="distinctive async marker message") as exc_info:
        await result.__anext__()

    assert type(exc_info.value) is ValueError


async def test_async_stream_result_silent_per_line_drop_not_detectable() -> None:
    """Per-line drops swallowed inside an async generator are invisible.

    iteration_errored stays False - async mirror of the sync StreamResult contract.
    """

    async def iter_with_silent_drop() -> AsyncIterator[str]:
        for item in ["record-1", "malformed", "record-2", "record-3"]:
            try:
                if item == "malformed":
                    raise ValueError("simulated parse failure")  # noqa: TRY301
                yield item
            except ValueError:
                pass

    result = AsyncStreamResult(iter_with_silent_drop())

    records = [item async for item in result]

    assert records == ["record-1", "record-2", "record-3"]
    assert result.record_count == 3
    assert not result.iteration_errored


# ---------------------------------------------------------------------------
# _require_env
# ---------------------------------------------------------------------------


def test_require_env_returns_value_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """_require_env returns the exact environment value when it is set and non-empty."""
    monkeypatch.setenv("TRACSS_TEST_VAR", "some-value")

    result = _require_env("TRACSS_TEST_VAR")

    assert result == "some-value"


def test_require_env_raises_naming_variable_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_require_env raises ValueError naming the missing variable when it is unset."""
    monkeypatch.delenv("TRACSS_TEST_VAR", raising=False)

    with pytest.raises(ValueError, match="TRACSS_TEST_VAR"):
        _require_env("TRACSS_TEST_VAR")


def test_require_env_treats_empty_string_as_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_require_env raises ValueError when the variable is set to an empty string."""
    monkeypatch.setenv("TRACSS_TEST_VAR", "")

    with pytest.raises(ValueError, match="TRACSS_TEST_VAR"):
        _require_env("TRACSS_TEST_VAR")


# ---------------------------------------------------------------------------
# _parse_token_response
# ---------------------------------------------------------------------------


def test_parse_token_response_happy_path_returns_token_and_future_expiry() -> None:
    """A well-formed payload returns the token and an expiry in the future."""
    before = time.monotonic()

    token, expires_at = _parse_token_response(
        {"access_token": FAKE_TOKEN, "expires_in": 3600}, TOKEN_URL
    )

    assert token == FAKE_TOKEN
    assert expires_at == pytest.approx(before + 3600 - 30, abs=1)


def test_parse_token_response_missing_access_token_raises_with_keys_listed() -> None:
    """Missing access_token raises ValueError listing the payload's actual keys."""
    payload = {"token_type": "Bearer", "expires_in": 3600}

    with pytest.raises(ValueError, match="access_token") as exc_info:
        _parse_token_response(payload, TOKEN_URL)

    assert "token_type" in str(exc_info.value)
    assert "expires_in" in str(exc_info.value)


def test_parse_token_response_empty_access_token_raises() -> None:
    """An empty-string access_token is treated the same as missing (falsy check)."""
    with pytest.raises(ValueError, match="access_token"):
        _parse_token_response({"access_token": ""}, TOKEN_URL)


def test_parse_token_response_missing_expires_in_defaults_to_3600s() -> None:
    """Omitting expires_in falls back to the 3600s default TTL."""
    before = time.monotonic()

    _token, expires_at = _parse_token_response({"access_token": FAKE_TOKEN}, TOKEN_URL)

    assert expires_at == pytest.approx(before + 3600 - 30, abs=1)


def test_parse_token_response_expires_in_zero_clamps_to_zero_not_default() -> None:
    """expires_in=0 must hit the clamp-to-zero branch, not the absent->default branch.

    This is the subtle `is not None` boundary: 0 is a present, falsy value, but
    the code checks `raw_expires_in is not None` rather than truthiness.
    """
    before = time.monotonic()

    _token, expires_at = _parse_token_response(
        {"access_token": FAKE_TOKEN, "expires_in": 0}, TOKEN_URL
    )

    # If 0 were mistaken for absent, expires_at would be ~before + 3570.
    assert expires_at == pytest.approx(before, abs=1)


def test_parse_token_response_negative_expires_in_clamps_to_zero() -> None:
    """A negative expires_in clamps to an immediately-expired token, not negative TTL."""
    before = time.monotonic()

    _token, expires_at = _parse_token_response(
        {"access_token": FAKE_TOKEN, "expires_in": -100}, TOKEN_URL
    )

    assert expires_at == pytest.approx(before, abs=1)


@pytest.mark.parametrize("expires_in", [1, 15, 29, 30, 31])
def test_parse_token_response_expiry_boundary_values_around_refresh_buffer(
    expires_in: int,
) -> None:
    """expires_at is always max(expires_in - 30, 0) seconds from now, at each boundary."""
    before = time.monotonic()

    _token, expires_at = _parse_token_response(
        {"access_token": FAKE_TOKEN, "expires_in": expires_in}, TOKEN_URL
    )

    expected_ttl = max(expires_in - 30, 0)
    assert expires_at == pytest.approx(before + expected_ttl, abs=1)


def test_parse_token_response_numeric_string_expires_in_coerces_to_int() -> None:
    """A numeric string expires_in ("3600") coerces via int() and behaves like the int."""
    before = time.monotonic()

    _token, expires_at = _parse_token_response(
        {"access_token": FAKE_TOKEN, "expires_in": "3600"}, TOKEN_URL
    )

    assert expires_at == pytest.approx(before + 3600 - 30, abs=1)


@pytest.mark.parametrize(
    "malformed_expires_in",
    ["not-a-number", [1, 2, 3]],
    ids=["non_numeric_string", "list"],
)
def test_parse_token_response_malformed_expires_in_logs_warning_and_uses_default(
    malformed_expires_in: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A malformed expires_in (int()-incompatible) logs a WARNING and falls back to 3600s.

    Exercises the `except (ValueError, TypeError)` branch - previously zero
    coverage. Distinct from the numeric-string case, which succeeds.
    """
    before = time.monotonic()

    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        _token, expires_at = _parse_token_response(
            {"access_token": FAKE_TOKEN, "expires_in": malformed_expires_in}, TOKEN_URL
        )

    assert expires_at == pytest.approx(before + 3600 - 30, abs=1)
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("not an integer" in r.message for r in warnings)


def test_parse_token_response_boolean_expires_in_coerces_via_int_true() -> None:
    """Documents current behavior: expires_in=True is coerced by int(True) == 1.

    Flagged ambiguity (plan item 3): bool is an int subclass in Python, so
    `int(True)` succeeds silently rather than raising TypeError/ValueError. An
    IdP response with "expires_in": true would produce a 1-second effective
    TTL with the short-lived-token warning firing (since 1 - 30 clamps to 0),
    but with no signal distinguishing this from a legitimately short-lived
    token. This is NOT asserted as correct behavior - just pinned as-is.
    """
    before = time.monotonic()

    token, expires_at = _parse_token_response(
        {"access_token": FAKE_TOKEN, "expires_in": True}, TOKEN_URL
    )

    assert token == FAKE_TOKEN
    assert expires_at == pytest.approx(before, abs=1)  # max(1 - 30, 0) == 0


def test_parse_token_response_short_lived_token_warns_when_effective_ttl_zero(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The short-lived-token warning fires iff effective TTL clamps to exactly 0."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        _parse_token_response({"access_token": FAKE_TOKEN, "expires_in": 30}, TOKEN_URL)

    warnings = [r.message for r in caplog.records if r.levelno == logging.WARNING]
    assert any("refresh buffer" in msg for msg in warnings)


def test_parse_token_response_normal_ttl_does_not_warn(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """No short-lived-token warning fires when effective TTL is > 0."""
    with caplog.at_level(logging.WARNING, logger="tracss.client"):
        _parse_token_response({"access_token": FAKE_TOKEN, "expires_in": 31}, TOKEN_URL)

    assert not any(r.levelno == logging.WARNING for r in caplog.records)


# ---------------------------------------------------------------------------
# _inject_json_accept
# ---------------------------------------------------------------------------


def test_inject_json_accept_injects_when_absent() -> None:
    """Accept: application/json is injected when no Accept header is present."""
    result = _inject_json_accept({})

    assert result["request_options"]["additional_headers"]["Accept"] == (
        "application/json"
    )


@pytest.mark.parametrize("casing", ["Accept", "accept", "ACCEPT"], ids=str)
def test_inject_json_accept_does_not_clobber_existing_header_any_casing(
    casing: str,
) -> None:
    """An explicit Accept header (any casing) is preserved, not overwritten."""
    kwargs = {"request_options": {"additional_headers": {casing: "application/xml"}}}

    result = _inject_json_accept(kwargs)

    headers = result["request_options"]["additional_headers"]
    assert headers[casing] == "application/xml"
    assert "Accept" not in headers or headers.get("Accept") == "application/xml"


def test_inject_json_accept_preserves_other_headers() -> None:
    """Unrelated headers already present in additional_headers are kept intact."""
    kwargs = {
        "request_options": {"additional_headers": {"X-Custom-Header": "custom-value"}}
    }

    result = _inject_json_accept(kwargs)

    headers = result["request_options"]["additional_headers"]
    assert headers["X-Custom-Header"] == "custom-value"
    assert headers["Accept"] == "application/json"


def test_inject_json_accept_does_not_mutate_input_kwargs() -> None:
    """The input kwargs dict is left unchanged - a new dict is returned instead."""
    original_request_options: dict[str, Any] = {}
    kwargs = {"format": "json", "request_options": original_request_options}

    _inject_json_accept(kwargs)

    assert kwargs["request_options"] is original_request_options
    assert original_request_options == {}
    assert kwargs == {"format": "json", "request_options": {}}


def test_inject_json_accept_handles_missing_request_options_key() -> None:
    """A kwargs dict with no 'request_options' key at all is handled cleanly."""
    kwargs = {"format": "json"}

    result = _inject_json_accept(kwargs)

    assert result["request_options"]["additional_headers"]["Accept"] == (
        "application/json"
    )


def test_inject_json_accept_handles_request_options_explicitly_none() -> None:
    """A kwargs dict with request_options=None (distinct shape) is handled cleanly."""
    kwargs = {"format": "json", "request_options": None}

    result = _inject_json_accept(kwargs)

    assert result["request_options"]["additional_headers"]["Accept"] == (
        "application/json"
    )


# ---------------------------------------------------------------------------
# _call_or_raw (sync)
# ---------------------------------------------------------------------------


def test_call_or_raw_defaults_format_to_json_when_absent() -> None:
    """_call_or_raw injects format='json' when the caller supplies no format kwarg."""
    captured: dict[str, Any] = {}

    def _capture(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "ok"

    _call_or_raw(_capture)

    assert captured["format"] == "json"


def test_call_or_raw_injects_accept_header_when_format_is_json() -> None:
    """_call_or_raw adds Accept: application/json when format resolves to json."""
    captured: dict[str, Any] = {}

    def _capture(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "ok"

    _call_or_raw(_capture)

    headers = captured["request_options"]["additional_headers"]
    assert headers["Accept"] == "application/json"


def test_call_or_raw_leaves_explicit_non_json_format_untouched() -> None:
    """An explicit non-json format is passed through unchanged, Accept is not injected."""
    captured: dict[str, Any] = {}

    def _capture(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "ok"

    _call_or_raw(_capture, format="KVN")

    assert captured["format"] == "KVN"
    assert "request_options" not in captured


def test_call_or_raw_returns_underlying_result_unchanged_on_success() -> None:
    """A successful call's return value is passed through unmodified."""
    sentinel = {"some": "typed-response"}

    result = _call_or_raw(lambda **_: sentinel)

    assert result is sentinel


def test_call_or_raw_converts_200_api_error_with_string_body_to_raw_response() -> None:
    """ApiError(status_code=200, body=str) is converted into a RawResponse."""

    def _raise(**_: Any) -> None:
        raise ApiError(status_code=HTTPStatus.OK, body="CCSDS_CDM_VERS = 1.0\n")

    result = _call_or_raw(_raise)

    assert isinstance(result, RawResponse)
    assert result.body == "CCSDS_CDM_VERS = 1.0\n"


@pytest.mark.parametrize(
    "status_code",
    [
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.NOT_FOUND,
        HTTPStatus.INTERNAL_SERVER_ERROR,
    ],
    ids=lambda sc: sc.name,
)
def test_call_or_raw_reraises_non_200_api_error_unchanged(
    status_code: HTTPStatus,
) -> None:
    """Any ApiError whose status_code is not 200 is re-raised unchanged."""

    def _raise(**_: Any) -> None:
        raise ApiError(status_code=status_code, body="error body")

    with pytest.raises(ApiError) as exc_info:
        _call_or_raw(_raise)

    assert exc_info.value.status_code == status_code


@pytest.mark.parametrize(
    "body",
    [None, b"binary content", {"partial": "json"}, ["a", "list"]],
    ids=["none", "bytes", "dict", "list"],
)
def test_call_or_raw_reraises_200_api_error_when_body_is_not_a_string(
    body: Any,
) -> None:
    """ApiError(200) is re-raised, not swallowed, when body isn't a string."""

    def _raise(**_: Any) -> None:
        raise ApiError(status_code=HTTPStatus.OK, body=body)

    with pytest.raises(ApiError) as exc_info:
        _call_or_raw(_raise)

    assert exc_info.value.status_code == HTTPStatus.OK
    assert exc_info.value.body == body


def test_call_or_raw_propagates_non_api_error_exceptions_untouched() -> None:
    """A non-ApiError exception (e.g. httpx.ConnectError) propagates untouched.

    There is no except clause for anything but ApiError.
    """

    def _raise(**_: Any) -> None:
        raise httpx.ConnectError("unreachable")

    with pytest.raises(httpx.ConnectError, match="unreachable"):
        _call_or_raw(_raise)


# ---------------------------------------------------------------------------
# _async_call_or_raw (async mirror - kept separate per policy)
# ---------------------------------------------------------------------------


async def test_async_call_or_raw_defaults_format_to_json_when_absent() -> None:
    """_async_call_or_raw injects format='json' when the caller supplies no format."""
    captured: dict[str, Any] = {}

    async def _capture(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "ok"

    await _async_call_or_raw(_capture)

    assert captured["format"] == "json"


async def test_async_call_or_raw_injects_accept_header_when_format_is_json() -> None:
    """_async_call_or_raw adds Accept: application/json when format resolves to json."""
    captured: dict[str, Any] = {}

    async def _capture(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "ok"

    await _async_call_or_raw(_capture)

    headers = captured["request_options"]["additional_headers"]
    assert headers["Accept"] == "application/json"


async def test_async_call_or_raw_leaves_explicit_non_json_format_untouched() -> None:
    """An explicit non-json format is passed through unchanged, Accept is not injected."""
    captured: dict[str, Any] = {}

    async def _capture(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "ok"

    await _async_call_or_raw(_capture, format="xml")

    assert captured["format"] == "xml"
    assert "request_options" not in captured


async def test_async_call_or_raw_returns_underlying_result_unchanged_on_success() -> None:
    """A successful call's return value is passed through unmodified."""
    sentinel = {"some": "typed-response"}

    async def _return_sentinel(**_: Any) -> dict[str, str]:
        return sentinel

    result = await _async_call_or_raw(_return_sentinel)

    assert result is sentinel


async def test_async_call_or_raw_converts_200_api_error_with_string_body() -> None:
    """ApiError(status_code=200, body=str) is converted into a RawResponse."""

    async def _raise(**_: Any) -> None:
        raise ApiError(status_code=HTTPStatus.OK, body="CCSDS_CDM_VERS = 1.0\n")

    result = await _async_call_or_raw(_raise)

    assert isinstance(result, RawResponse)
    assert result.body == "CCSDS_CDM_VERS = 1.0\n"


@pytest.mark.parametrize(
    "status_code",
    [
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.NOT_FOUND,
        HTTPStatus.INTERNAL_SERVER_ERROR,
    ],
    ids=lambda sc: sc.name,
)
async def test_async_call_or_raw_reraises_non_200_api_error_unchanged(
    status_code: HTTPStatus,
) -> None:
    """Any ApiError whose status_code is not 200 is re-raised unchanged."""

    async def _raise(**_: Any) -> None:
        raise ApiError(status_code=status_code, body="error body")

    with pytest.raises(ApiError) as exc_info:
        await _async_call_or_raw(_raise)

    assert exc_info.value.status_code == status_code


@pytest.mark.parametrize(
    "body",
    [None, b"binary content", {"partial": "json"}, ["a", "list"]],
    ids=["none", "bytes", "dict", "list"],
)
async def test_async_call_or_raw_reraises_200_api_error_when_body_not_a_string(
    body: Any,
) -> None:
    """ApiError(200) is re-raised, not swallowed, when body isn't a string."""

    async def _raise(**_: Any) -> None:
        raise ApiError(status_code=HTTPStatus.OK, body=body)

    with pytest.raises(ApiError) as exc_info:
        await _async_call_or_raw(_raise)

    assert exc_info.value.status_code == HTTPStatus.OK
    assert exc_info.value.body == body


async def test_async_call_or_raw_propagates_non_api_error_exceptions_untouched() -> None:
    """A non-ApiError exception (e.g. httpx.ConnectError) propagates untouched."""

    async def _raise(**_: Any) -> None:
        raise httpx.ConnectError("unreachable")

    with pytest.raises(httpx.ConnectError, match="unreachable"):
        await _async_call_or_raw(_raise)


# ---------------------------------------------------------------------------
# _OktaTokenMixin construction/validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("credential_value", [None, ""], ids=["missing", "empty"])
@pytest.mark.parametrize(
    "field", ["client_id", "client_secret"], ids=["client_id", "client_secret"]
)
def test_missing_or_empty_credential_raises(
    field: str,
    credential_value: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing (unset env, no kwarg) and empty-string credentials both raise ValueError.

    The two cases go through different branches with different message
    wording: a missing kwarg (None) falls through to _require_env, which
    names the env var (e.g. TRACSS_CLIENT_ID); an explicit empty string skips
    _require_env entirely and hits the dedicated empty-credential check, which
    names the kwarg (e.g. client_id). Both are ValueError - that's the
    behavioral contract this test pins - so the expected match pattern is
    selected per branch rather than asserting a single shared substring.
    """
    monkeypatch.delenv("TRACSS_CLIENT_ID", raising=False)
    monkeypatch.delenv("TRACSS_CLIENT_SECRET", raising=False)
    kwargs: dict[str, str | None] = {"client_id": "cid", "client_secret": "csec"}
    kwargs[field] = credential_value
    expected_match = f"TRACSS_{field.upper()}" if credential_value is None else field

    with pytest.raises(ValueError, match=expected_match):
        TraCSS(**kwargs)


def test_explicit_client_id_kwarg_overrides_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit client_id kwarg wins over TRACSS_CLIENT_ID env var."""
    monkeypatch.setenv("TRACSS_CLIENT_ID", "env-id")

    client = TraCSS(client_id="kwarg-id", client_secret="csec")

    assert client._client_id == "kwarg-id"


def test_explicit_client_secret_kwarg_overrides_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit client_secret kwarg wins over TRACSS_CLIENT_SECRET env var."""
    monkeypatch.setenv("TRACSS_CLIENT_SECRET", "env-secret")

    client = TraCSS(client_id="cid", client_secret="kwarg-secret")

    assert client._client_secret == "kwarg-secret"


def test_explicit_okta_domain_kwarg_overrides_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit okta_domain kwarg wins over TRACSS_OKTA_DOMAIN env var."""
    monkeypatch.setenv("TRACSS_OKTA_DOMAIN", "env-domain.example.com")

    client = TraCSS(
        client_id="cid", client_secret="csec", okta_domain="kwarg-domain.example.com"
    )

    assert client._okta_domain == "kwarg-domain.example.com"


def test_explicit_okta_auth_server_id_kwarg_overrides_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit okta_auth_server_id kwarg wins over TRACSS_OKTA_AUTH_SERVER_ID."""
    monkeypatch.setenv("TRACSS_OKTA_AUTH_SERVER_ID", "env-server-id")

    client = TraCSS(
        client_id="cid", client_secret="csec", okta_auth_server_id="kwarg-server-id"
    )

    assert client._okta_auth_server_id == "kwarg-server-id"


def test_explicit_okta_scope_kwarg_overrides_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit okta_scope kwarg wins over TRACSS_OKTA_SCOPE env var."""
    monkeypatch.setenv("TRACSS_OKTA_SCOPE", "env-scope")

    client = TraCSS(client_id="cid", client_secret="csec", okta_scope="kwarg-scope")

    assert client._okta_scope == "kwarg-scope"


def test_okta_domain_env_var_used_when_no_kwarg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TRACSS_OKTA_DOMAIN env var is used when no okta_domain kwarg is given."""
    monkeypatch.setenv("TRACSS_OKTA_DOMAIN", "env-domain.example.com")

    client = TraCSS(client_id="cid", client_secret="csec")

    assert client._okta_domain == "env-domain.example.com"


def test_okta_auth_server_id_env_var_used_when_no_kwarg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TRACSS_OKTA_AUTH_SERVER_ID env var is used when no kwarg is given."""
    monkeypatch.setenv("TRACSS_OKTA_AUTH_SERVER_ID", "env-server-id")

    client = TraCSS(client_id="cid", client_secret="csec")

    assert client._okta_auth_server_id == "env-server-id"


def test_okta_scope_env_var_used_when_no_kwarg(monkeypatch: pytest.MonkeyPatch) -> None:
    """TRACSS_OKTA_SCOPE env var is used when no okta_scope kwarg is given."""
    monkeypatch.setenv("TRACSS_OKTA_SCOPE", "env-scope")

    client = TraCSS(client_id="cid", client_secret="csec")

    assert client._okta_scope == "env-scope"


def test_okta_domain_defaults_used_when_neither_kwarg_nor_env_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Built-in defaults apply when neither kwarg nor env var supply Okta settings."""
    monkeypatch.delenv("TRACSS_OKTA_DOMAIN", raising=False)
    monkeypatch.delenv("TRACSS_OKTA_AUTH_SERVER_ID", raising=False)
    monkeypatch.delenv("TRACSS_OKTA_SCOPE", raising=False)

    client = TraCSS(client_id="cid", client_secret="csec")

    assert client._okta_domain == _OktaTokenMixin._DEFAULT_OKTA_DOMAIN
    assert client._okta_auth_server_id == _OktaTokenMixin._DEFAULT_AUTH_SERVER_ID
    assert client._okta_scope == _OktaTokenMixin._DEFAULT_SCOPE


def test_okta_domain_explicit_empty_string_raises() -> None:
    """An explicit empty-string okta_domain is rejected, unlike an omitted one.

    Distinct from omitting the kwarg (None), which falls back to env/default -
    an explicit "" is a deliberate misconfiguration, not "unset".
    """
    with pytest.raises(ValueError, match="okta_domain must not be empty"):
        TraCSS(client_id="cid", client_secret="csec", okta_domain="")


def test_okta_domain_with_url_scheme_raises() -> None:
    """A domain including a URL scheme (e.g. 'https://') is rejected."""
    with pytest.raises(ValueError, match="URL scheme"):
        TraCSS(client_id="cid", client_secret="csec", okta_domain="https://example.com")


def test_okta_domain_protocol_relative_scheme_not_caught() -> None:
    """Documents a source-level gap (plan ambiguity #2).

    The scheme check is a bare `"://" in okta_domain` substring test, so a
    protocol-relative value like '//evil.example.com' (no scheme token, no
    '://') is NOT caught, unlike a full 'https://...' value. This test pins
    current (arguably buggy) passthrough behavior rather than asserting it is
    correct - a source fix may be warranted.
    """
    client = TraCSS(
        client_id="cid", client_secret="csec", okta_domain="//evil.example.com"
    )

    assert client._okta_domain == "//evil.example.com"


@pytest.mark.parametrize(
    "domain_with_slashes",
    ["example.okta.com/", "example.okta.com//"],
    ids=["single_trailing_slash", "double_trailing_slash"],
)
def test_okta_domain_trailing_slashes_are_stripped(domain_with_slashes: str) -> None:
    """One or more trailing slashes on okta_domain are stripped."""
    client = TraCSS(
        client_id="cid", client_secret="csec", okta_domain=domain_with_slashes
    )

    assert client._okta_domain == "example.okta.com"


def test_okta_domain_whitespace_only_not_rejected() -> None:
    """Documents a source-level inconsistency (plan ambiguity #1).

    Unlike okta_scope, a whitespace-only okta_domain (e.g. "   ") passes the
    `not okta_domain` empty check (whitespace is truthy) and is NOT rejected,
    silently producing a broken token URL. This pins CURRENT behavior; it is
    not asserted to be correct, and a source fix may be warranted to reject
    whitespace-only domains the same way okta_scope does.
    """
    client = TraCSS(client_id="cid", client_secret="csec", okta_domain="   ")

    assert client._okta_domain == "   "  # not stripped/rejected - see docstring above


def test_okta_auth_server_id_empty_string_raises() -> None:
    """An explicit empty-string okta_auth_server_id is rejected."""
    with pytest.raises(ValueError, match="okta_auth_server_id"):
        TraCSS(client_id="cid", client_secret="csec", okta_auth_server_id="")


def test_okta_scope_whitespace_only_raises() -> None:
    """A whitespace-only okta_scope is rejected - previously zero coverage."""
    with pytest.raises(ValueError, match="okta_scope"):
        TraCSS(client_id="cid", client_secret="csec", okta_scope="   ")


def test_okta_scope_non_whitespace_only_is_stripped() -> None:
    """A okta_scope with surrounding whitespace is stripped, not rejected."""
    client = TraCSS(client_id="cid", client_secret="csec", okta_scope="  myscope  ")

    assert client._okta_scope == "myscope"


def test_initial_token_state_is_none_and_pre_expired() -> None:
    """A freshly constructed client has _token is None AND an already-expired expiry.

    Guards the lazy-fetch trigger condition
    `_token is None or time.monotonic() >= _token_expires_at`, not just one half of it.
    """
    client = TraCSS(client_id="cid", client_secret="csec")

    assert client._token is None
    assert client._token_expires_at < time.monotonic()


# ---------------------------------------------------------------------------
# TraCSS._get_token / _fetch_token (sync)
# ---------------------------------------------------------------------------


@respx.mock
def test_get_token_is_not_fetched_at_construction(respx_mock: respx.MockRouter) -> None:
    """Constructing TraCSS must not perform any Okta token fetch."""
    client = TraCSS(client_id="cid", client_secret="csec")

    assert client._token is None


@respx.mock
def test_get_token_fetches_lazily_on_first_call(respx_mock: respx.MockRouter) -> None:
    """The first call to _get_token triggers exactly one fetch and returns the token."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = TraCSS(client_id="cid", client_secret="csec")

    token = client._get_token()

    assert token == FAKE_TOKEN


@respx.mock
def test_get_token_reuses_cached_valid_token(respx_mock: respx.MockRouter) -> None:
    """A second call before expiry reuses the cached token - only one HTTP request."""
    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = TraCSS(client_id="cid", client_secret="csec")

    client._get_token()
    client._get_token()

    assert route.call_count == 1


@respx.mock
def test_get_token_refetches_after_expiry(respx_mock: respx.MockRouter) -> None:
    """An expired cached token triggers a fresh fetch returning the new token."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=_token_response(access_token="new-token")
    )
    client = TraCSS(client_id="cid", client_secret="csec")
    client._token = "old-token"
    client._token_expires_at = time.monotonic() - 1

    token = client._get_token()

    assert token == "new-token"


@respx.mock
def test_get_token_fetches_exactly_once_under_thread_contention(
    respx_mock: respx.MockRouter,
) -> None:
    """threading.Lock ensures only one Okta request fires under contention.

    threading.Barrier guarantees all threads reach _get_token simultaneously
    before any can acquire the lock, making contention deterministic.
    """
    barrier = threading.Barrier(10)

    def contended_fetch(client: TraCSS) -> None:
        barrier.wait()
        client._get_token()

    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = TraCSS(client_id="cid", client_secret="csec")
    threads = [
        threading.Thread(target=contended_fetch, args=(client,)) for _ in range(10)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert route.call_count == 1


@respx.mock
def test_fetch_token_sends_http_basic_auth_header(respx_mock: respx.MockRouter) -> None:
    """The token request carries HTTP Basic auth built from client_id:client_secret."""
    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = TraCSS(client_id="cid", client_secret="csec")

    client._get_token()

    expected = "Basic " + base64.b64encode(b"cid:csec").decode()
    assert route.calls[0].request.headers["authorization"] == expected


@respx.mock
def test_fetch_token_sends_grant_type_and_scope_in_form_body(
    respx_mock: respx.MockRouter,
) -> None:
    """The token request body is client_credentials grant with the configured scope."""
    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = TraCSS(client_id="cid", client_secret="csec", okta_scope="myscope")

    client._get_token()

    body = route.calls[0].request.content.decode()
    assert body == "grant_type=client_credentials&scope=myscope"


@respx.mock
def test_fetch_token_passes_configured_timeout_to_http_call(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_fetch_token passes the module-level Okta timeout constant to httpx.post."""
    import tracss.client as client_module

    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = TraCSS(client_id="cid", client_secret="csec")
    captured_kwargs: dict[str, Any] = {}
    original_post = httpx.post

    def _capturing_post(*args: Any, **kwargs: Any) -> httpx.Response:
        captured_kwargs.update(kwargs)
        return original_post(*args, **kwargs)

    monkeypatch.setattr(httpx, "post", _capturing_post)

    client._get_token()

    assert captured_kwargs["timeout"] == client_module._OKTA_TOKEN_TIMEOUT


@respx.mock
def test_fetch_token_401_raises_http_status_error(respx_mock: respx.MockRouter) -> None:
    """A 401 from Okta surfaces as httpx.HTTPStatusError, not a JSON/KeyError."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, text="Unauthorized")
    )
    client = TraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(httpx.HTTPStatusError):
        client._get_token()


@respx.mock
def test_fetch_token_connect_error_propagates(respx_mock: respx.MockRouter) -> None:
    """A network-level connect error during token fetch propagates to the caller."""
    respx_mock.post(TOKEN_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    client = TraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(httpx.ConnectError):
        client._get_token()


@respx.mock
def test_fetch_token_timeout_propagates(respx_mock: respx.MockRouter) -> None:
    """A timeout during token fetch propagates to the caller."""
    respx_mock.post(TOKEN_URL).mock(side_effect=httpx.TimeoutException("timed out"))
    client = TraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(httpx.TimeoutException):
        client._get_token()


@respx.mock
def test_fetch_token_non_json_200_raises_value_error_without_leaking_body(
    respx_mock: respx.MockRouter,
) -> None:
    """A non-JSON 200 Okta response raises ValueError whose message excludes the body.

    Security-sensitive per the docstring: the response body may contain
    sensitive IdP context and is logged at DEBUG only, never embedded in the
    raised exception's message.
    """
    secret_marker = "SECRET_IDP_CONTEXT_MARKER"
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=f"<html>{secret_marker}</html>")
    )
    client = TraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(ValueError, match="non-JSON") as exc_info:
        client._get_token()

    assert secret_marker not in str(exc_info.value)


# ---------------------------------------------------------------------------
# AsyncTraCSS._aget_token / _afetch_token (async mirror - kept separate)
# ---------------------------------------------------------------------------


async def test_aget_token_is_not_fetched_at_construction(
    respx_mock: respx.MockRouter,
) -> None:
    """Constructing AsyncTraCSS must not perform any Okta token fetch."""
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    assert client._token is None


@respx.mock
async def test_aget_token_fetches_lazily_on_first_call(
    respx_mock: respx.MockRouter,
) -> None:
    """The first call to _aget_token triggers exactly one fetch and returns the token."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    token = await client._aget_token()

    assert token == FAKE_TOKEN


@respx.mock
async def test_aget_token_reuses_cached_valid_token(
    respx_mock: respx.MockRouter,
) -> None:
    """A second call before expiry reuses the cached token - only one HTTP request."""
    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    await client._aget_token()
    await client._aget_token()

    assert route.call_count == 1


@respx.mock
async def test_aget_token_refetches_after_expiry(respx_mock: respx.MockRouter) -> None:
    """An expired cached token triggers a fresh fetch returning the new token."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=_token_response(access_token="new-async-token")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    client._token = "old-token"
    client._token_expires_at = time.monotonic() - 1

    token = await client._aget_token()

    assert token == "new-async-token"


@respx.mock
async def test_aget_token_fetches_exactly_once_under_async_contention(
    respx_mock: respx.MockRouter,
) -> None:
    """asyncio.Lock ensures only one Okta request fires under concurrent awaits.

    Uses an asyncio.Event gate instead of a sleep-based timing hack: each task
    signals arrival before calling _aget_token, and waits for all 10 arrivals
    before proceeding, so all 10 are guaranteed to race on the lock together
    (deterministic overlap, not dependent on scheduler timing). Note the gate
    must fire *before* _aget_token is entered, not inside the mocked HTTP
    response - the asyncio.Lock under test serializes access to the HTTP call
    itself, so only one task at a time could ever reach a gate placed there.
    """
    arrived = 0
    all_arrived = asyncio.Event()

    async def bump_and_wait() -> None:
        nonlocal arrived
        arrived += 1
        if arrived >= 10:
            all_arrived.set()
        await all_arrived.wait()

    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    async def contended_fetch() -> str:
        await bump_and_wait()
        return await client._aget_token()

    await asyncio.gather(*[contended_fetch() for _ in range(10)])

    assert route.call_count == 1


@respx.mock
async def test_afetch_token_sends_http_basic_auth_header(
    respx_mock: respx.MockRouter,
) -> None:
    """The async token request carries HTTP Basic auth built from client_id/secret."""
    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    await client._aget_token()

    expected = "Basic " + base64.b64encode(b"cid:csec").decode()
    assert route.calls[0].request.headers["authorization"] == expected


@respx.mock
async def test_afetch_token_sends_grant_type_and_scope_in_form_body(
    respx_mock: respx.MockRouter,
) -> None:
    """The async token request body is client_credentials grant with configured scope."""
    route = respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = AsyncTraCSS(client_id="cid", client_secret="csec", okta_scope="myscope")

    await client._aget_token()

    body = route.calls[0].request.content.decode()
    assert body == "grant_type=client_credentials&scope=myscope"


@respx.mock
async def test_afetch_token_passes_configured_timeout_to_http_call(
    respx_mock: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_afetch_token passes the module-level Okta timeout constant to the async client."""
    import tracss.client as client_module

    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    captured_kwargs: dict[str, Any] = {}
    original_post = httpx.AsyncClient.post

    async def _capturing_post(self: httpx.AsyncClient, *args: Any, **kwargs: Any) -> Any:
        captured_kwargs.update(kwargs)
        return await original_post(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "post", _capturing_post)

    await client._aget_token()

    assert captured_kwargs["timeout"] == client_module._OKTA_TOKEN_TIMEOUT


@respx.mock
async def test_afetch_token_401_raises_http_status_error(
    respx_mock: respx.MockRouter,
) -> None:
    """A 401 from Okta surfaces as httpx.HTTPStatusError."""
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, text="Unauthorized")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(httpx.HTTPStatusError):
        await client._aget_token()


@respx.mock
async def test_afetch_token_connect_error_propagates(
    respx_mock: respx.MockRouter,
) -> None:
    """A network-level connect error during async token fetch propagates."""
    respx_mock.post(TOKEN_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(httpx.ConnectError):
        await client._aget_token()


@respx.mock
async def test_afetch_token_timeout_propagates(respx_mock: respx.MockRouter) -> None:
    """A timeout during async token fetch propagates to the caller."""
    respx_mock.post(TOKEN_URL).mock(side_effect=httpx.TimeoutException("timed out"))
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(httpx.TimeoutException):
        await client._aget_token()


@respx.mock
async def test_afetch_token_non_json_200_raises_value_error_without_leaking_body(
    respx_mock: respx.MockRouter,
) -> None:
    """A non-JSON 200 async Okta response raises ValueError excluding the body."""
    secret_marker = "SECRET_IDP_CONTEXT_MARKER"
    respx_mock.post(TOKEN_URL).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=f"<html>{secret_marker}</html>")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(ValueError, match="non-JSON") as exc_info:
        await client._aget_token()

    assert secret_marker not in str(exc_info.value)


def test_async_tracss_get_token_raises_runtime_error() -> None:
    """AsyncTraCSS._get_token (sync accessor) raises RuntimeError.

    Directs callers to the async accessor instead - previously zero coverage.
    """
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    with pytest.raises(RuntimeError, match="_aget_token"):
        client._get_token()


def test_sync_token_noop_returns_empty_string_and_performs_no_io() -> None:
    """_sync_token_noop returns "" synchronously with no I/O.

    This is the mechanism that keeps AsyncTraCSS from blocking the event loop
    on the sync header-building path.
    """
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    result = client._sync_token_noop()

    assert result == ""


async def test_async_client_never_calls_sync_fetch_token(
    respx_mock: respx.MockRouter,
) -> None:
    """AsyncTraCSS must only call _afetch_token, never _fetch_token.

    Fern's async_get_headers() calls get_headers() (sync) before the async
    token path. If token=self._get_token were passed to AsyncBaseTraCSS,
    _fetch_token() would block the event loop on token expiry. Guards against
    that regression across a full async API call cycle.
    """
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    respx_mock.get("https://api.tracss.gov/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")
    sync_fetch_called = False

    def _guard_sync_fetch() -> tuple[str, float]:
        nonlocal sync_fetch_called
        sync_fetch_called = True
        return FAKE_TOKEN, 0.0

    client._fetch_token = _guard_sync_fetch  # type: ignore[method-assign]

    await client.subscriber.topics.list()

    assert not sync_fetch_called


# ---------------------------------------------------------------------------
# Sub-client lazy-init / locking - all 8 double-checked-locking properties
# ---------------------------------------------------------------------------


def _sync_sub_client_specs() -> list[tuple[str, str]]:
    """(container_attr, sub_attr) pairs for the 8 sync sub-clients."""
    return [
        ("metadata", "cdm"),
        ("metadata", "ocm"),
        ("metadata", "tip_reports"),
        ("bulk_data", "cdm"),
        ("bulk_data", "ocm"),
        ("bulk_data", "tip"),
        ("bulk_data", "announcements"),
        ("subscriber", "messages"),
    ]


@pytest.mark.parametrize(
    ("container_attr", "sub_attr"),
    _sync_sub_client_specs(),
    ids=[f"{c}.{s}" for c, s in _sync_sub_client_specs()],
)
def test_sub_client_lazy_init_memoizes_across_accesses(
    container_attr: str, sub_attr: str
) -> None:
    """Each sub-client property returns the same instance on repeated access."""
    client = TraCSS(client_id="cid", client_secret="csec")
    container = getattr(client, container_attr)

    first = getattr(container, sub_attr)
    second = getattr(container, sub_attr)

    assert first is second


@pytest.mark.parametrize(
    ("container_attr", "sub_attr"),
    _sync_sub_client_specs(),
    ids=[f"{c}.{s}" for c, s in _sync_sub_client_specs()],
)
def test_sub_client_lazy_init_initializes_exactly_once_under_thread_contention(
    container_attr: str, sub_attr: str
) -> None:
    """Threads racing on a sub-client property see it constructed exactly once."""
    client = TraCSS(client_id="cid", client_secret="csec")
    container = getattr(client, container_attr)
    barrier = threading.Barrier(8)
    results: list[Any] = []
    errors: list[BaseException] = []

    def access() -> None:
        try:
            barrier.wait()
            results.append(getattr(container, sub_attr))
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=access) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread raised an exception: {errors}"
    assert len({id(r) for r in results}) == 1, (
        "All threads must observe the same sub-client instance"
    )


# ---------------------------------------------------------------------------
# Bearer header wiring
# ---------------------------------------------------------------------------


@respx.mock
def test_sync_bearer_header_present_on_subscriber_call(
    respx_mock: respx.MockRouter,
) -> None:
    """Authorization: Bearer <token> is present and non-empty on a subscriber call."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    client = TraCSS(client_id="cid", client_secret="csec")

    client.subscriber.topics.list()

    auth = api_route.calls[0].request.headers["authorization"]
    assert auth == f"Bearer {FAKE_TOKEN}"


@respx.mock
def test_sync_bearer_header_present_on_metadata_call(
    respx_mock: respx.MockRouter,
) -> None:
    """Authorization: Bearer <token> is present and non-empty on a metadata call."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    client = TraCSS(client_id="cid", client_secret="csec")

    client.metadata.cdm.list()

    auth = api_route.calls[0].request.headers["authorization"]
    assert auth == f"Bearer {FAKE_TOKEN}"


@respx.mock
def test_sync_bearer_header_present_on_bulk_data_call(
    respx_mock: respx.MockRouter,
) -> None:
    """Authorization: Bearer <token> is present and non-empty on a bulk-data call."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/bulkdata/cdm/v2/stream").mock(
        return_value=httpx.Response(HTTPStatus.OK, text="")
    )
    client = TraCSS(client_id="cid", client_secret="csec")

    list(client.bulk_data.cdm.stream())

    auth = api_route.calls[0].request.headers["authorization"]
    assert auth == f"Bearer {FAKE_TOKEN}"


@respx.mock
async def test_async_bearer_header_present_on_subscriber_call(
    respx_mock: respx.MockRouter,
) -> None:
    """AsyncTraCSS subscriber calls carry the real token, never the noop placeholder."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    await client.subscriber.topics.list()

    auth = api_route.calls[0].request.headers["authorization"]
    assert auth == f"Bearer {FAKE_TOKEN}"
    assert auth not in ("Bearer ", "Bearer")


@respx.mock
async def test_async_bearer_header_present_on_metadata_call(
    respx_mock: respx.MockRouter,
) -> None:
    """AsyncTraCSS metadata calls carry the real token, never the noop placeholder."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    await client.metadata.cdm.list()

    auth = api_route.calls[0].request.headers["authorization"]
    assert auth == f"Bearer {FAKE_TOKEN}"


@respx.mock
async def test_async_bearer_header_present_on_bulk_data_call(
    respx_mock: respx.MockRouter,
) -> None:
    """AsyncTraCSS bulk-data calls carry the real token, never the noop placeholder."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/bulkdata/cdm/v2/stream").mock(
        return_value=httpx.Response(HTTPStatus.OK, text="")
    )
    client = AsyncTraCSS(client_id="cid", client_secret="csec")

    async for _ in client.bulk_data.cdm.stream():
        pass

    auth = api_route.calls[0].request.headers["authorization"]
    assert auth == f"Bearer {FAKE_TOKEN}"


@respx.mock
def test_default_base_url_is_api_tracss_gov(respx_mock: respx.MockRouter) -> None:
    """With no base_url override, requests go to the default https://api.tracss.gov."""
    respx_mock.post(TOKEN_URL).mock(return_value=_token_response())
    api_route = respx_mock.get("https://api.tracss.gov/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    client = TraCSS(client_id="cid", client_secret="csec")

    client.subscriber.topics.list()

    assert api_route.called
    assert str(api_route.calls[0].request.url).startswith("https://api.tracss.gov")


@respx.mock
def test_custom_base_url_overrides_default(respx_mock: respx.MockRouter) -> None:
    """An explicit base_url routes requests to the custom host, not api.tracss.gov."""
    api_route = respx_mock.get("http://mock.internal/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    client = TraCSS(
        client_id="cid", client_secret="csec", base_url="http://mock.internal"
    )
    client._token = FAKE_TOKEN
    client._token_expires_at = float("inf")

    client.subscriber.topics.list()

    assert api_route.called
    assert "api.tracss.gov" not in str(api_route.calls[0].request.url)
