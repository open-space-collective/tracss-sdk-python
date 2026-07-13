# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Metadata API client surface.

Exercises the `client.metadata.*` sub-clients end to end against a
respx-mocked transport. Several of these tests target the hand-written
wrapper behavior in `tracss/client.py` (`_MetadataWithJsonDefaults`,
`_JsonCdmClient`, `_JsonOcmClient`, `_JsonTipReportsClient`) as it is wired
through the public client - this is intentional; see the redesign plan.
"""

import io
import json
from http import HTTPStatus

import httpx
import pytest

from tests.conftest import maybe_await
from tracss.client import RawResponse
from tracss.core.api_error import ApiError
from tracss.metadata.cdm.types.list_by_operational_batch_cdm_response import (
    ListByOperationalBatchCdmResponse,
)
from tracss.metadata.cdm.types.list_cdm_response import ListCdmResponse
from tracss.metadata.conjunction_events.types.list_conjunction_events_response import (
    ListConjunctionEventsResponse,
)
from tracss.metadata.errors import (
    BadGatewayError,
    BadRequestError,
    ExpectationFailedError,
    ForbiddenError,
    InternalServerError,
    MethodNotAllowedError,
    NotFoundError,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnauthorizedError,
)
from tracss.metadata.ocm.types.list_ocm_response import ListOcmResponse

BASE = "https://api.tracss.gov"

# (status_code, expected exception class) for every status the generated
# metadata raw clients special-case. Confirmed identical across all
# metadata/*/raw_client.py by grep.
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


def _fake_ocm_file() -> tuple:
    return ("test.xml", io.BytesIO(b"<ocm/>"), "application/xml")


# ── Cross-cutting: error-status -> exception mapping ───────────────────────


@pytest.mark.parametrize(
    ("endpoint_path", "call"),
    [
        pytest.param(
            "/metadata/v2/tracssCdm",
            lambda c: c.metadata.cdm.list(),
            id="cdm_list",
        ),
        pytest.param(
            "/metadata/v2/ocm",
            lambda c: c.metadata.ocm.list(),
            id="ocm_list",
        ),
        pytest.param(
            "/metadata/tipReports",
            lambda c: c.metadata.tip_reports.list(),
            id="tip_reports_list",
        ),
        pytest.param(
            "/metadata/tracssCat",
            lambda c: c.metadata.tracss_cat.list(),
            id="tracss_cat_list",
        ),
        pytest.param(
            "/metadata/conjunctionDataEvents",
            lambda c: c.metadata.conjunction_events.list(),
            id="conjunction_events_list",
        ),
        pytest.param(
            "/metadata/announcements",
            lambda c: c.metadata.announcements.list(),
            id="announcements_list",
        ),
        pytest.param(
            "/metadata/schemas/xsd",
            lambda c: c.metadata.schemas.get_xsd(),
            id="schemas_get_xsd",
        ),
        pytest.param(
            "/metadata/space-track",
            lambda c: c.metadata.space_track.list(),
            id="space_track_list",
        ),
        pytest.param(
            "/metadata/v2/translationErrors",
            lambda c: c.metadata.translation_errors.list(),
            id="translation_errors_list",
        ),
        pytest.param(
            "/metadata/contactDirectory/operational/all",
            lambda c: c.metadata.contact_directory.list_operational(),
            id="contact_directory_list_operational",
        ),
    ],
)
@pytest.mark.parametrize(
    ("status_code", "expected_exception"), ERROR_STATUS_MATRIX, ids=ERROR_STATUS_IDS
)
@pytest.mark.asyncio
async def test_metadata_error_status_raises_mapped_exception(  # noqa: PLR0913
    client_kind, respx_mock, endpoint_path, call, status_code, expected_exception
):
    """Each metadata sub-service maps every documented error status to its exception."""
    respx_mock.get(f"{BASE}{endpoint_path}").mock(
        return_value=httpx.Response(status_code, json={"error": "problem"})
    )

    with pytest.raises(expected_exception) as exc_info:
        await maybe_await(call(client_kind))

    assert exc_info.value.status_code == status_code
    assert exc_info.value.body is not None


@pytest.mark.asyncio
async def test_metadata_unmapped_status_raises_generic_api_error(client_kind, respx_mock):
    """A status code not in the explicit if-chain (e.g. 418) falls through to ApiError.

    Confirmed from the bottom of every metadata raw_client.list method: after the
    explicit status-code checks, a JSON body is parsed and re-raised as a bare
    ApiError(status_code=..., body=...) with no special exception class.
    """
    respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(418, json={"error": "teapot"})
    )

    with pytest.raises(ApiError) as exc_info:
        await maybe_await(client_kind.metadata.cdm.list())

    assert exc_info.value.status_code == 418
    assert exc_info.value.body == {"error": "teapot"}


def test_api_error_str_includes_status_code_and_body():
    """ApiError.__str__ must surface headers, status_code, and body for debugging."""
    err = ApiError(headers={"x-req-id": "abc"}, status_code=500, body={"error": "boom"})

    text = str(err)

    assert "500" in text
    assert "boom" in text
    assert "abc" in text


# ── Format-defaulting matrix (cdm/ocm/tip_reports list + list_by_operational_batch) ──


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("call", "url_path", "expect_accept_header"),
    [
        pytest.param(
            lambda c: c.metadata.cdm.list(),
            "/metadata/v2/tracssCdm",
            True,
            id="cdm_list",
        ),
        pytest.param(
            lambda c: c.metadata.cdm.list_by_operational_batch(batch_id="b1"),
            "/metadata/v2/tracssCdmByOperationalBatch",
            False,
            id="cdm_list_by_operational_batch",
        ),
        pytest.param(
            lambda c: c.metadata.ocm.list(),
            "/metadata/v2/ocm",
            True,
            id="ocm_list",
        ),
        pytest.param(
            lambda c: c.metadata.tip_reports.list(),
            "/metadata/tipReports",
            True,
            id="tip_reports_list",
        ),
    ],
)
async def test_metadata_list_sends_json_format_by_default(
    client_kind, respx_mock, call, url_path, expect_accept_header
):
    """format=json is injected by default; Accept: application/json only where wired.

    _call_or_raw/_async_call_or_raw inject Accept only when format resolves to
    'json' AND the caller went through _inject_json_accept (cdm.list, ocm.list,
    tip_reports.list). cdm.list_by_operational_batch defaults format=json via
    setdefault but never calls _inject_json_accept. ocm.list_by_operational_batch
    is excluded from this matrix entirely: _JsonOcmClient.list_by_operational_batch
    only wraps the 204-handling behavior (see the dedicated 204 tests below) and
    never calls _call_or_raw, so it has no format-defaulting behavior at all.
    """
    route = respx_mock.get(f"{BASE}{url_path}").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(call(client_kind))

    assert "format=json" in str(route.calls[0].request.url)
    if expect_accept_header:
        assert route.calls[0].request.headers.get("accept") == "application/json"


def test_cdm_list_preserves_explicit_accept_header(api_client, respx_mock):
    """Caller-provided Accept header must not be overridden by _inject_json_accept.

    If a caller explicitly sets Accept: text/plain to request KVN, the guard
    in _inject_json_accept (case-insensitive any() check) must preserve it and
    not inject application/json.
    """
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, text="CCSDS_CDM_VERS = 1.0")
    )

    result = api_client.metadata.cdm.list(
        format="KVN",
        request_options={"additional_headers": {"Accept": "text/plain"}},
    )

    actual_accept = route.calls[0].request.headers.get("accept")
    assert actual_accept == "text/plain"
    assert isinstance(result, RawResponse)


# ── Non-JSON format -> RawResponse matrix ──────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("call", "url_path"),
    [
        pytest.param(
            lambda c, fmt: c.metadata.cdm.list(format=fmt),
            "/metadata/v2/tracssCdm",
            id="cdm_list",
        ),
        pytest.param(
            lambda c, fmt: c.metadata.ocm.list(format=fmt),
            "/metadata/v2/ocm",
            id="ocm_list",
        ),
        pytest.param(
            lambda c, fmt: c.metadata.tip_reports.list(format=fmt),
            "/metadata/tipReports",
            id="tip_reports_list",
        ),
    ],
)
@pytest.mark.parametrize("fmt", ["KVN", "xml", "csv"])
async def test_metadata_list_non_json_format_returns_raw_response(
    client_kind, respx_mock, call, url_path, fmt
):
    """Non-JSON format values return a RawResponse and round-trip verbatim in the URL.

    csv is only a real option for CDM per the spec, but the wrapper applies the
    same format=/RawResponse logic uniformly regardless of endpoint, so testing
    it across all three list endpoints pins that uniform behavior.
    """
    body = f"SOME_FIELD = value ({fmt})"
    route = respx_mock.get(f"{BASE}{url_path}").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=body)
    )

    result = await maybe_await(call(client_kind, fmt))

    assert isinstance(result, RawResponse)
    assert str(result) == body
    assert f"format={fmt}" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_metadata_list_propagates_non_200_api_error(client_kind, respx_mock):
    """Non-200 ApiErrors (4xx, 5xx) must not be swallowed by _call_or_raw."""
    respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN, json={"error": "forbidden"})
    )

    with pytest.raises(ForbiddenError) as exc_info:
        await maybe_await(client_kind.metadata.cdm.list())

    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


# ── OCM batch 204 handling ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ocm_list_by_operational_batch_returns_empty_list_on_204(
    client_kind, respx_mock
):
    """HTTP 204 No Content from list_by_operational_batch must return [] not raise.

    The live API returns 204 when no batches match the query instead of 200 + [].
    The generated SDK tries to parse an empty body as JSON and raises ApiError(204).
    _JsonOcmClient/_AsyncJsonOcmClient catch this and return an empty list.
    """
    respx_mock.get(f"{BASE}/metadata/v2/ocm/operationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )

    result = await maybe_await(client_kind.metadata.ocm.list_by_operational_batch())

    assert result == []


@pytest.mark.asyncio
async def test_ocm_list_by_operational_batch_propagates_non_204_api_error(
    client_kind, respx_mock
):
    """Non-204 errors (e.g. 401) must still propagate unchanged."""
    respx_mock.get(f"{BASE}/metadata/v2/ocm/operationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, json={"error": "unauth"})
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        await maybe_await(client_kind.metadata.ocm.list_by_operational_batch())

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED


# ── CDM/OCM list 204 handling (empty result set) ────────────────────────────
#
# Live-confirmed 2026-07-12: every metadata list endpoint answers HTTP 204 with
# an empty body when no records match, not 200 + empty payload. The generated
# parser treats 204 as 2xx, calls .json() on the empty body, and raises
# ApiError(204); _empty_on_204 substitutes an empty typed response so an ordinary
# "no matches" query does not surface as an exception.


@pytest.mark.asyncio
async def test_ocm_list_returns_empty_response_on_204(client_kind, respx_mock):
    """HTTP 204 (empty OCM result set) must return an empty ListOcmResponse, not raise."""
    respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )

    result = await maybe_await(client_kind.metadata.ocm.list())

    assert isinstance(result, ListOcmResponse)
    assert result.headers_only is None
    assert result.default is None


@pytest.mark.asyncio
async def test_cdm_list_returns_empty_response_on_204(client_kind, respx_mock):
    """HTTP 204 (empty CDM result set) must return an empty ListCdmResponse, not raise."""
    respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )

    result = await maybe_await(client_kind.metadata.cdm.list())

    assert isinstance(result, ListCdmResponse)
    assert result.headers_only is None


@pytest.mark.asyncio
async def test_cdm_list_by_operational_batch_returns_empty_response_on_204(
    client_kind, respx_mock
):
    """HTTP 204 from CDM list_by_operational_batch must return an empty typed response."""
    respx_mock.get(f"{BASE}/metadata/v2/tracssCdmByOperationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )

    result = await maybe_await(
        client_kind.metadata.cdm.list_by_operational_batch(batch_id="nomatch")
    )

    assert isinstance(result, ListByOperationalBatchCdmResponse)


@pytest.mark.asyncio
async def test_ocm_list_propagates_non_204_api_error(client_kind, respx_mock):
    """Non-204 errors from ocm.list must still propagate, not be swallowed as empty."""
    respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, json={"error": "unauth"})
    )

    with pytest.raises(UnauthorizedError):
        await maybe_await(client_kind.metadata.ocm.list())


# ── Empty-result sentinels on the JSON-only metadata list endpoints ─────────
# Live-confirmed 2026-07-12: these controllers signal "no matching records" with a
# per-controller sentinel (204 for space_track/conjunction_events, 404 + text for
# tracss_cat/contact_directory), not 200 []. The empty-safe wrappers translate that
# to an empty result instead of raising.


@pytest.mark.asyncio
async def test_space_track_list_returns_empty_on_204(client_kind, respx_mock):
    respx_mock.get(f"{BASE}/metadata/space-track").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )
    assert await maybe_await(client_kind.metadata.space_track.list()) == []


@pytest.mark.asyncio
async def test_space_track_list_nested_returns_empty_on_204(client_kind, respx_mock):
    respx_mock.get(f"{BASE}/metadata/space-track-nested").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )
    assert await maybe_await(client_kind.metadata.space_track.list_nested()) == []


@pytest.mark.asyncio
async def test_conjunction_events_list_returns_empty_on_204(client_kind, respx_mock):
    respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )
    result = await maybe_await(client_kind.metadata.conjunction_events.list())
    assert isinstance(result, ListConjunctionEventsResponse)


@pytest.mark.asyncio
async def test_tracss_cat_list_returns_empty_on_404_sentinel(client_kind, respx_mock):
    respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(HTTPStatus.NOT_FOUND, text="No TracssCat(s) found.")
    )
    assert await maybe_await(client_kind.metadata.tracss_cat.list()) == []


@pytest.mark.asyncio
async def test_tracss_cat_list_propagates_genuine_404(client_kind, respx_mock):
    """A 404 without the empty-sentinel message must still raise (not be masked)."""
    respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(HTTPStatus.NOT_FOUND, text="Route not found")
    )
    with pytest.raises(ApiError) as exc_info:
        await maybe_await(client_kind.metadata.tracss_cat.list())
    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_contact_directory_list_operational_returns_empty_on_404_sentinel(
    client_kind, respx_mock
):
    respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(HTTPStatus.NOT_FOUND, text="No contacts found")
    )
    result = await maybe_await(client_kind.metadata.contact_directory.list_operational())
    assert result == []


# ── OCM upload ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ocm_upload_is_post_to_v2(client_kind, respx_mock):
    """upload() must POST to the v2 upload path."""
    route = respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(client_kind.metadata.ocm.upload(file=_fake_ocm_file()))

    assert route.calls[0].request.method == "POST"


@pytest.mark.asyncio
async def test_ocm_upload_sends_multipart_form_data(client_kind, respx_mock):
    """upload() must encode the file as multipart/form-data under the 'file' field name.

    Pins the actual wire encoding (force_multipart=True, files={"file": file} in
    ocm/raw_client.py), not just method/path - a prior version of this test only
    checked the HTTP method and never verified the multipart shape.
    """
    route = respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(client_kind.metadata.ocm.upload(file=_fake_ocm_file()))

    request = route.calls[0].request
    content_type = request.headers.get("content-type", "")
    assert content_type.startswith("multipart/form-data")
    assert b'name="file"' in request.content
    assert b"<ocm/>" in request.content


@pytest.mark.asyncio
async def test_ocm_upload_sends_trigger_ca_as_query_param(client_kind, respx_mock):
    """The triggerCA param must be forwarded as a query param, not a header."""
    route = respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(
        client_kind.metadata.ocm.upload(file=_fake_ocm_file(), trigger_ca=True)
    )

    assert "triggerCA=true" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_ocm_upload_sends_update_database_as_header(client_kind, respx_mock):
    """The updateDatabase param must be sent as an HTTP header, not a query param."""
    route = respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(
        client_kind.metadata.ocm.upload(file=_fake_ocm_file(), update_database="true")
    )

    request = route.calls[0].request
    assert "updatedatabase" in {k.lower() for k in request.headers}
    assert "updateDatabase" not in str(request.url)


@pytest.mark.asyncio
async def test_ocm_upload_returns_dict_on_json_2xx(client_kind, respx_mock):
    """A JSON 2xx response body must be returned as a dict."""
    respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.CREATED, json={"status": "ok"})
    )

    result = await maybe_await(client_kind.metadata.ocm.upload(file=_fake_ocm_file()))

    assert isinstance(result, dict)
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_ocm_upload_returns_str_on_text_plain_2xx(client_kind, respx_mock):
    """A text/plain 2xx response body (spec allows both for 201) is returned as str."""
    respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(
            HTTPStatus.CREATED, text="Uploaded OCM(s) Successfully"
        )
    )

    result = await maybe_await(client_kind.metadata.ocm.upload(file=_fake_ocm_file()))

    assert isinstance(result, str)
    assert result == "Uploaded OCM(s) Successfully"


@pytest.mark.asyncio
async def test_ocm_upload_error_status_raises_mapped_exception(client_kind, respx_mock):
    """upload() must map error statuses the same way as list endpoints."""
    respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.BAD_REQUEST, json={"error": "bad"})
    )

    with pytest.raises(BadRequestError) as exc_info:
        await maybe_await(client_kind.metadata.ocm.upload(file=_fake_ocm_file()))

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST


# ── TraCSS CAT ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tracss_cat_list_returns_list_of_dicts_for_json_array_response(
    client_kind, respx_mock
):
    """list() is plain generated code typed List[Dict] - no dict-wrapping wrapper exists.

    Unlike bulk_data.announcements (which has a hand-written wrapper coercing a
    bare dict into a single-element list), metadata.tracss_cat.list has no such
    override: it is unmodified Fern-generated code that calls construct_type
    against List[Dict[str, Any]] and returns whatever shape the server sent.
    """
    payload = [{"noradId": "12345", "name": "SAT-1"}, {"noradId": "67890"}]
    respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=payload)
    )

    result = await maybe_await(client_kind.metadata.tracss_cat.list())

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["noradId"] == "12345"


def test_tracss_cat_list_partial_args(api_client, respx_mock):
    """Optional filter kwargs must be forwarded as their camelCase query params."""
    route = respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    api_client.metadata.tracss_cat.list(
        norad_id="12345",
        organization="Acme",
        satellite_name="SAT-1",
        object_type="PAYLOAD",
        orbital_regime="LEO",
        count_only=True,
        headers_only=False,
    )

    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "organization=Acme" in url
    assert "satelliteName=SAT-1" in url
    assert "objectType=PAYLOAD" in url
    assert "orbitalRegime=LEO" in url
    assert "countOnly=true" in url
    assert "headersOnly=false" in url


@pytest.mark.asyncio
async def test_tracss_cat_upload_csv_sends_multipart_file(client_kind, respx_mock):
    """upload_csv() attaches the CSV as a multipart/form-data `file` field.

    The tracssCat CSV upload body is patched in `make specs` from a bare binary
    string to a named `file` object property (see DEVELOPMENT.md), matching the
    working ocm.upload shape, so Fern generates a `file=` parameter that is
    transmitted as multipart/form-data.
    """
    import io

    route = respx_mock.post(f"{BASE}/metadata/tracssCat/update/csv").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(
        client_kind.metadata.tracss_cat.upload_csv(
            file=("cat.csv", io.BytesIO(b"noradId\n12345\n"), "text/csv")
        )
    )

    request = route.calls[0].request
    assert request.method == "POST"
    assert "multipart/form-data" in request.headers["content-type"]
    assert b"noradId" in request.content


# ── Contact Directory ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_contact_directory_list_operational_returns_list(client_kind, respx_mock):
    """Override in metadata-overrides.yaml pins the response type to a typed list."""
    from tracss.metadata.types import OperationalContactInfoDto

    payload = [
        {
            "satelliteOwnershipGroup": "Acme Sat Co",
            "satellites": [{"noradId": 12345, "name": "ACME-1"}],
            "contacts": [{"name": "John Doe", "email": "john@acme.com"}],
        }
    ]
    respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=payload)
    )

    result = await maybe_await(client_kind.metadata.contact_directory.list_operational())

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], OperationalContactInfoDto)


def test_contact_directory_list_operational_optional_filters(api_client, respx_mock):
    """norad_id and organization must be forwarded as query params."""
    route = respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    api_client.metadata.contact_directory.list_operational(
        norad_id="12345", organization="Acme"
    )

    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "organization=Acme" in url


@pytest.mark.asyncio
async def test_contact_directory_update_operational_sends_put_with_json_body(
    client_kind, respx_mock
):
    """update_operational must PUT the given request dict as the JSON body."""
    route = respx_mock.put(f"{BASE}/metadata/contactDirectory/operational/update").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    await maybe_await(
        client_kind.metadata.contact_directory.update_operational(
            request={"name": "John", "email": "john@acme.com"}
        )
    )

    request = route.calls[0].request
    assert request.method == "PUT"
    assert json.loads(request.content) == {"name": "John", "email": "john@acme.com"}


# ── Schemas ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "url_path"),
    [
        pytest.param("get_xsd", "/metadata/schemas/xsd", id="get_xsd"),
        pytest.param("get_json", "/metadata/schemas/json", id="get_json"),
    ],
)
async def test_schemas_get_returns_list_of_schema_response(
    client_kind, respx_mock, method_name, url_path
):
    """get_xsd/get_json behave identically: both return list[SchemaResponse]."""
    from tracss.metadata.types.schema_response import SchemaResponse

    schemas = [
        {"name": "cdm.xsd", "url": "https://api.tracss.gov/metadata/schemas/cdm.xsd"},
        {"name": "ocm.xsd", "url": "https://api.tracss.gov/metadata/schemas/ocm.xsd"},
    ]
    respx_mock.get(f"{BASE}{url_path}").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=schemas)
    )
    method = getattr(client_kind.metadata.schemas, method_name)

    result = await maybe_await(method())

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], SchemaResponse)
    assert result[0].url is not None
    assert "cdm.xsd" in result[0].url


# ── Conjunction Events ────────────────────────────────────────────────────────


def test_conjunction_events_list_returns_typed_response(api_client, respx_mock):
    """list() must return a ListConjunctionEventsResponse, not a raw dict."""
    from tracss.metadata.conjunction_events.types import ListConjunctionEventsResponse

    respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"default": []})
    )

    result = api_client.metadata.conjunction_events.list()

    assert isinstance(result, ListConjunctionEventsResponse)


@pytest.mark.parametrize(
    ("kwarg", "query_key", "value"),
    [
        ("object1object_designator", "object1ObjectDesignator", "12345"),
        ("object2object_designator", "object2ObjectDesignator", "67890"),
        ("min_tca", "minTca", "2024-01-01T00:00:00Z"),
        ("max_tca", "maxTca", "2024-12-31T00:00:00Z"),
        ("min_miss_distance", "minMissDistance", "10"),
        ("max_miss_distance", "maxMissDistance", "5000"),
        ("min_collision_probability", "minCollisionProbability", "0.0001"),
        ("max_collision_probability", "maxCollisionProbability", "0.01"),
        ("creation_date", "creationDate", "2024-06-01"),
        ("conjunction_data_event_id", "conjunctionDataEventId", "abc-123"),
        ("sort", "sort", "tca"),
        ("sort_direction", "sortDirection", "desc"),
        ("size", "size", 5),
        ("page", "page", 2),
        ("headers_only", "headersOnly", True),
    ],
)
def test_conjunction_events_list_forwards_each_optional_kwarg(
    api_client, respx_mock, kwarg, query_key, value
):
    """Each optional filter/sort/pagination kwarg is forwarded individually."""
    route = respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    api_client.metadata.conjunction_events.list(**{kwarg: value})

    query = httpx.QueryParams(route.calls[0].request.url.query)
    expected_value = "true" if value is True else str(value)
    assert query.get(query_key) == expected_value


def test_conjunction_events_list_kitchen_sink(api_client, respx_mock):
    """All optional kwargs combined must all appear in the outgoing query string."""
    route = respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    api_client.metadata.conjunction_events.list(
        object1object_designator="12345",
        object2object_designator="67890",
        min_tca="2024-01-01T00:00:00Z",
        max_tca="2024-12-31T00:00:00Z",
        min_miss_distance="10",
        max_miss_distance="5000",
        min_collision_probability="0.0001",
        max_collision_probability="0.01",
        creation_date="2024-06-01",
        conjunction_data_event_id="abc-123",
        sort="tca",
        sort_direction="desc",
        size=5,
        page=2,
        headers_only=True,
    )

    query = httpx.QueryParams(route.calls[0].request.url.query)
    for query_key, expected in [
        ("object1ObjectDesignator", "12345"),
        ("object2ObjectDesignator", "67890"),
        ("minTca", "2024-01-01T00:00:00Z"),
        ("maxTca", "2024-12-31T00:00:00Z"),
        ("minMissDistance", "10"),
        ("maxMissDistance", "5000"),
        ("minCollisionProbability", "0.0001"),
        ("maxCollisionProbability", "0.01"),
        ("creationDate", "2024-06-01"),
        ("conjunctionDataEventId", "abc-123"),
        ("sort", "tca"),
        ("sortDirection", "desc"),
        ("size", "5"),
        ("page", "2"),
        ("headersOnly", "true"),
    ]:
        assert query.get(query_key) == expected


@pytest.mark.parametrize(
    "operator_value",
    [
        pytest.param(">2024-01-01", id="greater_than"),
        pytest.param("<2024-01-01", id="less_than"),
        pytest.param(">=2024-01-01", id="greater_than_or_equal"),
        pytest.param("<=2024-01-01", id="less_than_or_equal"),
        pytest.param("<>SAT-1", id="not_equal"),
        pytest.param("*SAT", id="like"),
        pytest.param("~*SAT", id="not_like"),
        pytest.param("12345,67890", id="in_list"),
        pytest.param("12345...67890", id="between"),
    ],
)
def test_conjunction_events_list_operator_syntax_survives_verbatim(
    api_client, respx_mock, operator_value
):
    """The filter-operator mini-language must round-trip through query encoding unchanged.

    conjunction_data_event_id's docstring documents comma-list and this endpoint
    shares the same mini-language (=, <>, *Value, ~*Value, >, <, >=, <=, In, Between)
    as subscriber.messages.list's filter_designators. Only normal per-character URL
    percent-encoding should apply - no client-side reinterpretation of the operator.
    """
    route = respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    api_client.metadata.conjunction_events.list(conjunction_data_event_id=operator_value)

    sent_value = httpx.QueryParams(route.calls[0].request.url.query).get(
        "conjunctionDataEventId"
    )
    assert sent_value == operator_value


def test_conjunction_events_list_error_status_raises_mapped_exception(
    api_client, respx_mock
):
    """4xx/5xx errors from the conjunction events endpoint propagate as mapped errors."""
    respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, json={"error": "unauth"})
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        api_client.metadata.conjunction_events.list()

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED


# ── Announcements (metadata) ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_announcements_list_returns_list(client_kind, respx_mock):
    """list() must return a Python list of SpaceTrackAnnouncement objects."""
    from tracss.metadata.types import SpaceTrackAnnouncement

    payload = [
        {"id": "1", "announcementType": "INFORMATION", "announcementText": "Test msg"}
    ]
    respx_mock.get(f"{BASE}/metadata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=payload)
    )

    result = await maybe_await(client_kind.metadata.announcements.list())

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], SpaceTrackAnnouncement)


def test_announcements_list_optional_filters(api_client, respx_mock):
    """announcement_type and size must be forwarded as query params."""
    route = respx_mock.get(f"{BASE}/metadata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    api_client.metadata.announcements.list(announcement_type="OPERATIONAL", size=10)

    url = str(route.calls[0].request.url)
    assert "announcementType=OPERATIONAL" in url
    assert "size=10" in url


def test_announcements_list_error_status_raises_mapped_exception(api_client, respx_mock):
    """4xx errors from the announcements endpoint must propagate as mapped exceptions."""
    respx_mock.get(f"{BASE}/metadata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.UNAUTHORIZED, json={"error": "unauth"})
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        api_client.metadata.announcements.list()

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED


# ── Space Track (previously zero coverage) ────────────────────────────────────


@pytest.mark.asyncio
async def test_space_track_list_path_and_typed_response(client_kind, respx_mock):
    """space_track.list() GETs the space-track path and returns typed SpaceTrack items."""
    from tracss.metadata.types.space_track import SpaceTrack

    route = respx_mock.get(f"{BASE}/metadata/space-track").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[{"correlationId": "abc-123"}])
    )

    result = await maybe_await(client_kind.metadata.space_track.list())

    assert route.called
    assert isinstance(result, list)
    assert isinstance(result[0], SpaceTrack)


def test_space_track_list_forwards_id_query_param(api_client, respx_mock):
    """The optional id filter must be forwarded as a query param."""
    route = respx_mock.get(f"{BASE}/metadata/space-track").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    api_client.metadata.space_track.list(id="abc-123")

    assert "id=abc-123" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_space_track_list_nested_path_and_typed_response(client_kind, respx_mock):
    """space_track.list_nested() must GET the nested path and return typed items."""
    from tracss.metadata.types.space_track_nested_dto import SpaceTrackNestedDto

    route = respx_mock.get(f"{BASE}/metadata/space-track-nested").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[{"correlationId": "abc-123"}])
    )

    result = await maybe_await(client_kind.metadata.space_track.list_nested())

    assert route.called
    assert isinstance(result, list)
    assert isinstance(result[0], SpaceTrackNestedDto)


def test_space_track_list_error_status_raises_mapped_exception(api_client, respx_mock):
    """Error statuses on space_track.list must map through the same exception matrix."""
    respx_mock.get(f"{BASE}/metadata/space-track").mock(
        return_value=httpx.Response(HTTPStatus.NOT_FOUND, json={"error": "missing"})
    )

    with pytest.raises(NotFoundError) as exc_info:
        api_client.metadata.space_track.list()

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


# ── Translation Errors (previously zero coverage) ─────────────────────────────


@pytest.mark.asyncio
async def test_translation_errors_list_path_and_typed_response(client_kind, respx_mock):
    """translation_errors.list() GETs the v2 path and returns typed response rows."""
    from tracss.metadata.types.ocm_metadata_v2dto import OcmMetadataV2Dto

    route = respx_mock.get(f"{BASE}/metadata/v2/translationErrors").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[{"messageId": "OCM_1"}])
    )

    result = await maybe_await(client_kind.metadata.translation_errors.list())

    assert route.called
    assert isinstance(result, list)
    assert isinstance(result[0], OcmMetadataV2Dto)


def test_translation_errors_list_forwards_optional_filters(api_client, respx_mock):
    """message_id, satellite_id, and run_id must be forwarded as query params."""
    route = respx_mock.get(f"{BASE}/metadata/v2/translationErrors").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )

    api_client.metadata.translation_errors.list(
        message_id="OCM_202605142222", satellite_id=43129, run_id="run-1"
    )

    url = str(route.calls[0].request.url)
    assert "messageId=OCM_202605142222" in url
    assert "satelliteId=43129" in url
    assert "runId=run-1" in url


def test_translation_errors_list_error_status_raises_mapped_exception(
    api_client, respx_mock
):
    """Error statuses on translation_errors.list must map through the exception matrix."""
    respx_mock.get(f"{BASE}/metadata/v2/translationErrors").mock(
        return_value=httpx.Response(HTTPStatus.BAD_REQUEST, json={"error": "bad"})
    )

    with pytest.raises(BadRequestError) as exc_info:
        api_client.metadata.translation_errors.list()

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST


# ── Sub-client wiring regression guards ────────────────────────────────────────


def test_metadata_property_returns_json_defaults_subclass(api_client):
    """client.metadata must be the wrapper subclass, not the plain generated one."""
    from tracss.client import _MetadataWithJsonDefaults

    assert isinstance(api_client.metadata, _MetadataWithJsonDefaults)


@pytest.mark.asyncio
async def test_async_metadata_property_returns_json_defaults_subclass(async_api_client):
    """AsyncTraCSS.metadata must be the async wrapper subclass."""
    from tracss.client import _AsyncMetadataWithJsonDefaults

    assert isinstance(async_api_client.metadata, _AsyncMetadataWithJsonDefaults)


def test_metadata_tip_reports_returns_json_defaults_subclass(api_client):
    """client.metadata.tip_reports must be the JSON-defaulting wrapper subclass."""
    from tracss.client import _JsonTipReportsClient

    assert isinstance(api_client.metadata.tip_reports, _JsonTipReportsClient)


@pytest.mark.asyncio
async def test_async_metadata_tip_reports_returns_json_defaults_subclass(
    async_api_client,
):
    """AsyncTraCSS.metadata.tip_reports must be the async JSON-defaulting wrapper."""
    from tracss.client import _AsyncJsonTipReportsClient

    assert isinstance(async_api_client.metadata.tip_reports, _AsyncJsonTipReportsClient)
