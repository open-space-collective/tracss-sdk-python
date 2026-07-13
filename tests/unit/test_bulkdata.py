# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Bulk Data API client surface (cdm, ocm, tip, announcements).

Covers the hand-written ``StreamResult``/``AsyncStreamResult`` wrapping
applied to cdm/ocm/tip ``stream()`` (see ``sdks/python/tracss/client.py``),
plus the generated ``announcements.list()`` response shape (corrected via a
response schema override in ``bulkdata-overrides.yaml``, no wrapper needed).
The underlying NDJSON parsing loop in ``bulk_data/*/raw_client.py`` is
generated but is exercised here too since ``StreamResult`` depends directly on
its silent-exception-swallowing contract.
"""

from http import HTTPStatus

import httpx
import pytest

from tests.conftest import maybe_await
from tracss.bulk_data.errors.bad_gateway_error import BadGatewayError
from tracss.bulk_data.errors.bad_request_error import BadRequestError
from tracss.bulk_data.errors.expectation_failed_error import ExpectationFailedError
from tracss.bulk_data.errors.forbidden_error import ForbiddenError
from tracss.bulk_data.errors.internal_server_error import InternalServerError
from tracss.bulk_data.errors.method_not_allowed_error import MethodNotAllowedError
from tracss.bulk_data.errors.not_found_error import NotFoundError
from tracss.bulk_data.errors.service_unavailable_error import ServiceUnavailableError
from tracss.bulk_data.errors.too_many_requests_error import TooManyRequestsError
from tracss.bulk_data.errors.unauthorized_error import UnauthorizedError
from tracss.core.api_error import ApiError

BASE = "https://api.tracss.gov"

STREAM_URLS = {
    "cdm": f"{BASE}/bulkdata/cdm/v2/stream",
    "ocm": f"{BASE}/bulkdata/ocm/v2/stream",
    "tip": f"{BASE}/bulkdata/tip/stream",
}

# (status_code, expected exception class) - identical across cdm/ocm/tip/announcements
# raw_client.py error branches (verified by grep: all four check this exact set).
ERROR_STATUS_MATRIX = [
    (HTTPStatus.BAD_REQUEST, BadRequestError),
    (HTTPStatus.UNAUTHORIZED, UnauthorizedError),
    (HTTPStatus.FORBIDDEN, ForbiddenError),
    (HTTPStatus.NOT_FOUND, NotFoundError),
    (HTTPStatus.METHOD_NOT_ALLOWED, MethodNotAllowedError),
    (HTTPStatus.EXPECTATION_FAILED, ExpectationFailedError),
    (HTTPStatus.TOO_MANY_REQUESTS, TooManyRequestsError),
    (HTTPStatus.INTERNAL_SERVER_ERROR, InternalServerError),
    (HTTPStatus.BAD_GATEWAY, BadGatewayError),
    (HTTPStatus.SERVICE_UNAVAILABLE, ServiceUnavailableError),
]
ERROR_STATUS_IDS = [cls.__name__ for _, cls in ERROR_STATUS_MATRIX]
error_status_matrix = pytest.mark.parametrize(
    ("status", "expected_exc"), ERROR_STATUS_MATRIX, ids=ERROR_STATUS_IDS
)


def _stream_of(client, endpoint: str, **kwargs):
    """Return the StreamResult/AsyncStreamResult for `endpoint` on `client`."""
    return getattr(client.bulk_data, endpoint).stream(**kwargs)


# ── Param serialization ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "case",
    [
        ("cdm", "message_id", "MSG-001", "messageId=MSG-001"),
        ("cdm", "correlation_id", "abc-123", "correlationId=abc-123"),
        ("cdm", "tca", ">2024-01-01T00:00:00Z", "tca="),
        ("cdm", "message_for", "IRIDIUM 161", "messageFor="),
        ("cdm", "miss_distance", "<100", "missDistance="),
        ("cdm", "collision_probability", ">0.0001", "collisionProbability="),
        ("cdm", "headers_only", True, "headersOnly=true"),
        ("cdm", "size", 50, "size=50"),
        ("cdm", "page", 2, "page=2"),
        ("cdm", "format", "json", "format=json"),
        ("ocm", "constellation", "STARLINK", "constellation=STARLINK"),
        ("ocm", "created_by", "18 SDS", "createdBy="),
        ("ocm", "object_designator", "45678", "objectDesignator=45678"),
        ("ocm", "operator", "STARLINK", "operator=STARLINK"),
        ("ocm", "owner", "SPACEX", "owner=SPACEX"),
        ("ocm", "start_time", "2024-01-01T00:00:00Z", "startTime="),
        ("ocm", "stop_time", "2024-02-01T00:00:00Z", "stopTime="),
        ("ocm", "traj_basis", "CALCULATED", "trajBasis=CALCULATED"),
        ("ocm", "max_creation_date", "2024-01-01", "maxCreationDate="),
        ("ocm", "size", 25, "size=25"),
        ("ocm", "page", 1, "page=1"),
        ("tip", "norad_id", "12345", "noradId=12345"),
        ("tip", "id", "999", "id=999"),
        ("tip", "msg_epoch", "2024-01-01T00:00:00Z", "msgEpoch="),
        ("tip", "window", "3600", "window=3600"),
        ("tip", "rev", "42", "rev=42"),
        ("tip", "direction", "ascending", "direction=ascending"),
        ("tip", "latitude", "10.5", "latitude=10.5"),
        ("tip", "longitude", "-20.5", "longitude=-20.5"),
        ("tip", "inclination", "51.6", "inclination=51.6"),
        ("tip", "next_report", "24", "nextReport=24"),
        ("tip", "high_interest", "Y", "highInterest=Y"),
        ("tip", "size", 10, "size=10"),
        ("tip", "page", 3, "page=3"),
    ],
    ids=lambda c: f"{c[0]}-{c[1]}",
)
def test_stream_forwards_single_optional_kwarg_as_camel_case_query_param(
    api_client, respx_mock, case
):
    """Each optional stream filter kwarg is serialized as its camelCase query key."""
    endpoint, kwarg, value, expected_query = case
    route = respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text="")
    )

    list(_stream_of(api_client, endpoint, **{kwarg: value}))

    url = str(route.calls[0].request.url)
    assert expected_query in url


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
def test_stream_no_args_issues_bare_get_request(api_client, respx_mock, endpoint):
    """Calling stream() with no filters still issues a plain GET."""
    route = respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text="")
    )

    list(_stream_of(api_client, endpoint))

    assert route.called
    assert route.calls[0].request.method == "GET"


# ── NDJSON parsing ───────────────────────────────────────────────────────────
#
# cdm/ocm yield pydantic UncheckedBaseModel instances built via
# `model_construct(**obj)`, which does NOT run field validation - so a
# "fails Pydantic validation" line for those two is really a TypeError from
# `**obj` requiring a mapping (confirmed by direct construct_type() probing).
# tip's response type is `typing.Any`, so construct_type() returns whatever
# json.loads() produced unchanged, and a non-dict line yields successfully.


@pytest.mark.parametrize("endpoint", ["cdm", "ocm"])
def test_stream_valid_ndjson_line_parses_into_typed_record_with_expected_fields(
    api_client, respx_mock, endpoint
):
    """A single well-formed NDJSON line yields a record with the expected field values.

    `headersOnly` and `default` are the only fields declared on StreamCdmResponse/
    StreamOcmResponse; `objectDesignator` lands as an extra (`model_extra`) field
    since the model allows extras rather than raising on unknown keys.
    """
    body = '{"headersOnly": "false", "default": "value", "objectDesignator": "45678"}\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    records = list(_stream_of(api_client, endpoint))

    assert len(records) == 1
    assert records[0].headers_only == "false"
    assert records[0].default == "value"
    assert records[0].model_extra == {"objectDesignator": "45678"}


def test_tip_stream_valid_ndjson_line_parses_into_plain_dict(api_client, respx_mock):
    """TIP's stream response type is typing.Any, so a valid line yields a plain dict."""
    body = '{"noradId": "12345", "highInterest": "Y"}\n'
    respx_mock.get(STREAM_URLS["tip"]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    records = list(_stream_of(api_client, "tip"))

    assert records == [{"noradId": "12345", "highInterest": "Y"}]


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
def test_stream_blank_lines_between_records_are_skipped(api_client, respx_mock, endpoint):
    """Blank lines interleaved with NDJSON records are skipped, not counted as records."""
    body = '\n\n{"headersOnly": "true"}\n\n{"headersOnly": "false"}\n\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = _stream_of(api_client, endpoint)
    records = list(result)

    assert len(records) == 2
    assert result.record_count == 2


@pytest.mark.parametrize("endpoint", ["cdm", "ocm"])
def test_stream_malformed_json_line_is_silently_dropped(api_client, respx_mock, endpoint):
    """A line that isn't valid JSON is dropped; surrounding valid lines still yield."""
    body = '{"headersOnly": "true"}\n{not valid json\n{"headersOnly": "false"}\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = _stream_of(api_client, endpoint)
    records = list(result)

    assert [r.headers_only for r in records] == ["true", "false"]
    assert result.record_count == 2
    assert not result.iteration_errored


def test_tip_stream_malformed_json_line_is_silently_dropped(api_client, respx_mock):
    """TIP: a malformed-JSON line is dropped; surrounding valid lines still yield."""
    body = '{"noradId": "1"}\n{not valid json\n{"noradId": "2"}\n'
    respx_mock.get(STREAM_URLS["tip"]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = _stream_of(api_client, "tip")
    records = list(result)

    assert records == [{"noradId": "1"}, {"noradId": "2"}]
    assert not result.iteration_errored


@pytest.mark.parametrize("endpoint", ["cdm", "ocm"])
def test_stream_line_failing_record_construction_is_silently_dropped(
    api_client, respx_mock, endpoint
):
    """A syntactically valid JSON line that can't become the record type is dropped.

    cdm/ocm records use pydantic's `model_construct(**obj)`, which skips field
    validation entirely (confirmed: a wrong-typed known field is accepted
    as-is). The one way construction still fails is when the top-level JSON
    value isn't an object at all (`**obj` then raises TypeError), e.g. a bare
    JSON array line. That TypeError is caught by the same
    `except Exception: pass` as a malformed-JSON line.
    """
    body = '{"headersOnly": "true"}\n[1, 2, 3]\n{"headersOnly": "false"}\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = _stream_of(api_client, endpoint)
    records = list(result)

    assert [r.headers_only for r in records] == ["true", "false"]
    assert result.record_count == 2
    assert not result.iteration_errored


# ── Async NDJSON parsing (mirrors sync; separate per streaming policy) ──────


@pytest.mark.parametrize("endpoint", ["cdm", "ocm"])
async def test_async_stream_valid_ndjson_line_parses_into_typed_record(
    async_api_client, respx_mock, endpoint
):
    """Async: a well-formed NDJSON line yields a record with the expected field values."""
    body = '{"headersOnly": "false", "default": "value", "objectDesignator": "45678"}\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    records = [r async for r in _stream_of(async_api_client, endpoint)]

    assert len(records) == 1
    assert records[0].headers_only == "false"
    assert records[0].default == "value"
    assert records[0].model_extra == {"objectDesignator": "45678"}


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
async def test_async_stream_blank_lines_are_skipped(
    async_api_client, respx_mock, endpoint
):
    """Async: blank lines interleaved with NDJSON records don't affect record_count."""
    body = '\n\n{"headersOnly": "true"}\n\n{"headersOnly": "false"}\n\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = _stream_of(async_api_client, endpoint)
    records = [r async for r in result]

    assert len(records) == 2
    assert result.record_count == 2


@pytest.mark.parametrize("endpoint", ["cdm", "ocm"])
async def test_async_stream_malformed_json_line_is_silently_dropped(
    async_api_client, respx_mock, endpoint
):
    """Async: a malformed-JSON line is dropped; surrounding valid lines still yield."""
    body = '{"headersOnly": "true"}\n{not valid json\n{"headersOnly": "false"}\n'
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = _stream_of(async_api_client, endpoint)
    records = [r async for r in result]

    assert [r.headers_only for r in records] == ["true", "false"]
    assert not result.iteration_errored


# ── Streaming error paths (sync) ────────────────────────────────────────────


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
@error_status_matrix
def test_stream_error_status_sets_iteration_errored_and_raises_mapped_exception(
    api_client, respx_mock, endpoint, status, expected_exc
):
    """Every mapped error status raises its specific exception and sets iteration_errored.

    Covers cdm/ocm/tip together since their raw_client error branches are
    identical (confirmed by grep across all three).
    """
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(status, json={"error": "failure"})
    )

    result = _stream_of(api_client, endpoint)
    with pytest.raises(expected_exc):
        list(result)

    assert result.iteration_errored
    assert result.record_count == 0


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
def test_stream_unmapped_error_status_raises_generic_api_error(
    api_client, respx_mock, endpoint
):
    """A status with no dedicated exception class (e.g. 418) falls back to ApiError."""
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.IM_A_TEAPOT, json={"error": "teapot"})
    )

    result = _stream_of(api_client, endpoint)
    with pytest.raises(ApiError) as exc_info:
        list(result)

    assert exc_info.value.status_code == HTTPStatus.IM_A_TEAPOT
    assert exc_info.value.body == {"error": "teapot"}
    assert result.iteration_errored


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
def test_stream_clean_exhaustion_does_not_set_iteration_errored(
    api_client, respx_mock, endpoint
):
    """A stream that exhausts normally (even zero records) must not report an error."""
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.OK, text="")
    )

    result = _stream_of(api_client, endpoint)
    list(result)

    assert not result.iteration_errored


# ── Streaming error paths (async) ───────────────────────────────────────────


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
@error_status_matrix
async def test_async_stream_error_status_raises_mapped_exception(
    async_api_client, respx_mock, endpoint, status, expected_exc
):
    """Async mirror: mapped error statuses raise their exception, set iteration_errored.

    Covers cdm/ocm/tip together on AsyncStreamResult (see the sync version for
    why these three are one equivalence class).
    """
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(status, json={"error": "failure"})
    )

    result = _stream_of(async_api_client, endpoint)
    with pytest.raises(expected_exc):
        async for _ in result:
            pass

    assert result.iteration_errored
    assert result.record_count == 0


@pytest.mark.parametrize("endpoint", ["cdm", "ocm", "tip"])
async def test_async_stream_unmapped_error_status_raises_generic_api_error(
    async_api_client, respx_mock, endpoint
):
    """Async: an unmapped status code (e.g. 418) falls back to the generic ApiError."""
    respx_mock.get(STREAM_URLS[endpoint]).mock(
        return_value=httpx.Response(HTTPStatus.IM_A_TEAPOT, json={"error": "teapot"})
    )

    result = _stream_of(async_api_client, endpoint)
    with pytest.raises(ApiError) as exc_info:
        async for _ in result:
            pass

    assert exc_info.value.status_code == HTTPStatus.IM_A_TEAPOT
    assert result.iteration_errored


# ── announcements.list ──────────────────────────────────────────────────────


@pytest.mark.parametrize("kind", ["sync", "async"])
async def test_announcements_list_is_get(api_client, async_api_client, respx_mock, kind):
    """announcements.list issues a GET regardless of client flavor."""
    client = api_client if kind == "sync" else async_api_client
    route = respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    await maybe_await(client.bulk_data.announcements.list())

    assert route.called
    assert route.calls[0].request.method == "GET"


async def test_announcements_list_returns_json_array_not_bare_string(
    client_kind, respx_mock
):
    """A 2xx JSON array body is returned as a list, not a repr'd string.

    The spec originally declared `content: */*` with `schema: {type: string}`
    for this endpoint, which Fern's generated raw client mapped to `str` via
    `construct_type(type_=str, ...)` - silently stringifying the array. A
    response schema override in `bulkdata-overrides.yaml` corrects this so
    Fern generates the right list type directly.
    """
    respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json=[{"type": "INFORMATION", "id": "1"}]
        )
    )

    result = await maybe_await(client_kind.bulk_data.announcements.list())

    assert isinstance(result, list)
    assert result == [{"type": "INFORMATION", "id": "1"}]


async def test_announcements_list_returns_empty_list_for_empty_array(
    client_kind, respx_mock
):
    """An empty JSON array body round-trips as an empty list, not a wrapped [[]]."""
    respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    result = await maybe_await(client_kind.bulk_data.announcements.list())

    assert result == []


async def test_announcements_list_optional_type_param_is_forwarded(
    client_kind, respx_mock
):
    """The optional `type` filter is forwarded verbatim as a query param."""
    route = respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    await maybe_await(client_kind.bulk_data.announcements.list(type="OPERATIONAL"))

    url = str(route.calls[0].request.url)
    assert "type=OPERATIONAL" in url


async def test_announcements_list_optional_size_param_is_forwarded(
    client_kind, respx_mock
):
    """The optional `size` filter is forwarded verbatim as a query param."""
    route = respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    await maybe_await(client_kind.bulk_data.announcements.list(size=25))

    url = str(route.calls[0].request.url)
    assert "size=25" in url


@error_status_matrix
async def test_announcements_list_error_status_raises_mapped_exception(
    client_kind, respx_mock, status, expected_exc
):
    """announcements.list maps every documented error status to its specific exception.

    status_code and body must be populated on the raised exception.
    """
    respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(status, json={"error": "failure"})
    )

    with pytest.raises(expected_exc) as exc_info:
        await maybe_await(client_kind.bulk_data.announcements.list())

    assert exc_info.value.status_code == status
    assert exc_info.value.body == {"error": "failure"}


async def test_announcements_list_unmapped_error_status_raises_generic_api_error(
    client_kind, respx_mock
):
    """An unmapped status code (e.g. 418) falls back to the generic ApiError."""
    respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.IM_A_TEAPOT, json={"error": "teapot"})
    )

    with pytest.raises(ApiError) as exc_info:
        await maybe_await(client_kind.bulk_data.announcements.list())

    assert exc_info.value.status_code == HTTPStatus.IM_A_TEAPOT
    assert exc_info.value.body == {"error": "teapot"}
