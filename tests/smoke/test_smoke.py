# SPDX-License-Identifier: Apache-2.0
"""Smoke tests against the live TraCSS API.

These tests require real credentials in the environment:
  export TRACSS_CLIENT_ID=...
  export TRACSS_CLIENT_SECRET=...

Run via: make smoke
"""

from http import HTTPStatus

import httpx
import pytest

from tracss.bulk_data.cdm.types import StreamCdmResponse
from tracss.client import RawResponse
from tracss.core.api_error import ApiError
from tracss.metadata.cdm.types import ListCdmResponse
from tracss.metadata.conjunction_events.types import ListConjunctionEventsResponse
from tracss.metadata.ocm.types import ListOcmResponse

# Status codes meaning "these credentials lack subscriber access", not an SDK bug.
# Per-namespace error classes differ, so guard on base ApiError + status_code.
_ACCESS_DENIED_STATUSES = frozenset(
    {HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}
)


@pytest.mark.smoke
def test_subscriber_topics_list(live_client):
    try:
        result = live_client.subscriber.topics.list()
    except ApiError as exc:
        if exc.status_code in _ACCESS_DENIED_STATUSES:
            pytest.skip("credentials lack subscriber access")
        raise
    assert isinstance(result, str)


@pytest.mark.smoke
def test_subscriber_get_offset(live_client, live_topics):
    if not live_topics:
        pytest.skip("no subscriber topics available or credentials lack access")
    result = live_client.subscriber.topics.get_offset(topic=live_topics[0])
    assert result is not None


@pytest.mark.smoke
def test_subscriber_messages_list(live_client, live_topics):
    if not live_topics:
        pytest.skip("no subscriber topics available or credentials lack access")
    result = live_client.subscriber.messages.list(topic=live_topics[0], offset=0)
    assert result is not None


@pytest.mark.smoke
def test_metadata_cdm_list(live_client):
    result = live_client.metadata.cdm.list(size=1)
    assert isinstance(result, ListCdmResponse)


@pytest.mark.smoke
def test_metadata_cdm_raw_format(live_client):
    result = live_client.metadata.cdm.list(size=1, format="KVN")
    assert isinstance(result, RawResponse), (
        f"Expected RawResponse for format='KVN', got {type(result).__name__}"
    )


@pytest.mark.smoke
def test_metadata_ocm_list(live_client):
    result = live_client.metadata.ocm.list(size=1)
    assert isinstance(result, ListOcmResponse)


@pytest.mark.smoke
def test_metadata_announcements_list(live_client):
    result = live_client.metadata.announcements.list(size=1)
    assert isinstance(result, list)


@pytest.mark.smoke
def test_bulkdata_cdm_stream(live_client):
    result = live_client.bulk_data.cdm.stream(size=1)
    records = list(result)  # exhaust the iterator so record_count is populated
    assert not result.iteration_errored, "CDM stream raised an error during iteration"
    assert result.record_count >= 0
    if result.record_count == 0:
        pytest.skip("CDM stream returned 0 records - data may not be available")
    # Regression guard for the bulk-vs-metadata content-negotiation asymmetry:
    # bulk streams return application/x-ndjson under the default Accept (live-
    # confirmed 2026-07-12) and are NOT format=json-forced like the metadata
    # wrappers. If the server ever defaulted to KVN text instead, every line would
    # fail to parse and be silently dropped (record_count would fall to 0). A
    # returned record therefore proves NDJSON was parsed into a typed model.
    assert isinstance(records[0], StreamCdmResponse), (
        f"CDM stream record is {type(records[0]).__name__}, not a parsed "
        "StreamCdmResponse - the stream may be returning KVN text instead of NDJSON"
    )


@pytest.mark.smoke
def test_bulkdata_ocm_stream(live_client):
    result = live_client.bulk_data.ocm.stream(size=1)
    list(result)
    assert not result.iteration_errored, "OCM stream raised an error during iteration"
    assert result.record_count >= 0


@pytest.mark.smoke
def test_bulkdata_tip_stream(live_client):
    result = live_client.bulk_data.tip.stream(size=1)
    list(result)
    assert not result.iteration_errored, "TIP stream raised an error during iteration"
    assert result.record_count >= 0


@pytest.mark.smoke
def test_bulkdata_announcements_list(live_client):
    result = live_client.bulk_data.announcements.list(size=1)
    assert isinstance(result, list)


@pytest.mark.smoke
def test_metadata_ocm_upload(live_client):
    import io

    result = live_client.metadata.ocm.upload(
        file=("smoke_test.xml", io.BytesIO(b"<ocm/>"), "application/xml")
    )
    assert isinstance(result, (dict, str)), (
        f"metadata.ocm.upload() returned unexpected type {type(result).__name__}; "
        "expected dict (JSON 201) or str (text/plain 201)"
    )


@pytest.mark.smoke
def test_metadata_tip_reports_list(live_client):
    result = live_client.metadata.tip_reports.list(size=1)
    assert not isinstance(result, RawResponse), (
        "tip_reports.list() returned RawResponse, format=json default not applied"
    )


@pytest.mark.smoke
def test_metadata_tracss_cat_list(live_client):
    result = live_client.metadata.tracss_cat.list(size=1)
    assert isinstance(result, list)


@pytest.mark.smoke
def test_metadata_space_track_list(live_client):
    result = live_client.metadata.space_track.list()
    assert isinstance(result, list)


@pytest.mark.smoke
def test_metadata_space_track_list_nested(live_client):
    result = live_client.metadata.space_track.list_nested()
    assert isinstance(result, list)


@pytest.mark.smoke
def test_metadata_schemas_get_xsd(live_client):
    result = live_client.metadata.schemas.get_xsd()
    assert isinstance(result, list), (
        f"Expected list[str] from schemas.get_xsd(), got {type(result).__name__}. "
        "If the live API returns non-JSON, add a _RawSchemaClient wrapper."
    )


@pytest.mark.smoke
def test_metadata_schemas_get_json(live_client):
    result = live_client.metadata.schemas.get_json()
    assert isinstance(result, list), (
        f"Expected list[str] from schemas.get_json(), got {type(result).__name__}. "
        "If the live API returns non-JSON, add a _RawSchemaClient wrapper."
    )


@pytest.mark.smoke
def test_metadata_conjunction_events_list(live_client):
    try:
        result = live_client.metadata.conjunction_events.list(size=1, headers_only=True)
    except httpx.ReadTimeout:
        pytest.skip("conjunction_events endpoint timed out, no data available")
    assert isinstance(result, ListConjunctionEventsResponse)
    # headers_only=True must route to the headers_only field, not default
    assert result.default is None, (
        "headers_only=True returned data in the 'default' field, routing is broken"
    )


@pytest.mark.smoke
def test_metadata_contact_directory_list_operational(live_client):
    result = live_client.metadata.contact_directory.list_operational()
    assert isinstance(result, list)


# ── Empty-result guards ───────────────────────────────────────────────────────
# These query each empty-safe list endpoint with a filter that matches nothing and
# assert an empty result is returned rather than an exception. They are the only
# regression guard for the per-controller empty-result sentinels (204 for
# space_track/conjunction_events, 404 + English text for tracss_cat/contact_directory);
# Prism mock tests cannot reproduce the live 404-text behavior. If TraCSS changes the
# 404 message, the substring guard in _empty_on_not_found silently stops matching and
# these tests turn red - update the sentinel and the message together.

_IMPOSSIBLE_ID = "=999999999"


@pytest.mark.smoke
def test_metadata_space_track_list_empty(live_client):
    result = live_client.metadata.space_track.list(id=_IMPOSSIBLE_ID)
    assert result == [], f"expected [] on empty 204, got {result!r}"


@pytest.mark.smoke
def test_metadata_space_track_list_nested_empty(live_client):
    result = live_client.metadata.space_track.list_nested(id=_IMPOSSIBLE_ID)
    assert result == [], f"expected [] on empty 204, got {result!r}"


@pytest.mark.smoke
def test_metadata_tracss_cat_list_empty(live_client):
    # 404 "No TracssCat(s) found." sentinel -> [] via _empty_on_not_found
    result = live_client.metadata.tracss_cat.list(satellite_name="=ZZZNONEXISTENT")
    assert result == [], f"expected [] on empty 404 sentinel, got {result!r}"


@pytest.mark.smoke
def test_metadata_contact_directory_list_operational_empty(live_client):
    # 404 "No contacts found" sentinel -> [] via _empty_on_not_found
    result = live_client.metadata.contact_directory.list_operational(
        norad_id=_IMPOSSIBLE_ID
    )
    assert result == [], f"expected [] on empty 404 sentinel, got {result!r}"


@pytest.mark.smoke
def test_metadata_conjunction_events_list_empty(live_client):
    try:
        result = live_client.metadata.conjunction_events.list(
            conjunction_data_event_id=_IMPOSSIBLE_ID, size=1
        )
    except httpx.ReadTimeout:
        pytest.skip("conjunction_events endpoint timed out")
    assert isinstance(result, ListConjunctionEventsResponse)
    # CR-1: an empty result must expose iterable [] fields, not None, so callers can
    # iterate result.default without a TypeError guard.
    assert result.default == [], f"expected default=[] on empty, got {result.default!r}"
    assert result.headers_only == [], (
        f"expected headers_only=[] on empty, got {result.headers_only!r}"
    )
