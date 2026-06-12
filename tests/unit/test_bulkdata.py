# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Bulk Data API client surface."""

import httpx
import respx

BASE = "https://api.tracss.gov"


def test_cdm_stream_no_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/cdm/v2/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(api_client.bulk_data.cdm.stream())
    assert route.called
    assert route.calls[0].request.method == "GET"


def test_cdm_stream_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/cdm/v2/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(
        api_client.bulk_data.cdm.stream(
            tca=">2024-01-01T00:00:00Z", message_for="IRIDIUM 161"
        )
    )
    url = str(route.calls[0].request.url)
    assert "tca=" in url
    assert "messageFor=" in url


def test_cdm_stream_full_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/cdm/v2/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(
        api_client.bulk_data.cdm.stream(
            message_id="MSG-001",
            tca=">2024-01-01T00:00:00Z",
            miss_distance="<100",
            collision_probability=">0.0001",
            size=50,
            page=2,
        )
    )
    url = str(route.calls[0].request.url)
    assert "messageId=MSG-001" in url
    assert "missDistance=" in url
    assert "collisionProbability=" in url
    assert "size=50" in url
    assert "page=2" in url


def test_cdm_stream_v1_uses_v1_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/cdm/v1/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(api_client.bulk_data.cdm.stream_v1())
    assert route.called


def test_ocm_stream_uses_v2_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/ocm/v2/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(api_client.bulk_data.ocm.stream())
    assert route.called


def test_ocm_stream_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/ocm/v2/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(api_client.bulk_data.ocm.stream(operator="STARLINK", object_designator="45678"))
    url = str(route.calls[0].request.url)
    assert "operator=STARLINK" in url
    assert "objectDesignator=45678" in url


def test_ocm_stream_v1_uses_v1_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/ocm/v1/stream").mock(
        return_value=httpx.Response(200, text="")
    )
    list(api_client.bulk_data.ocm.stream_v1())
    assert route.called


def test_tip_stream_no_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/tip/stream").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.bulk_data.tip.stream()
    assert route.called
    assert route.calls[0].request.method == "GET"


def test_tip_stream_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/tip/stream").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.bulk_data.tip.stream(norad_id="12345", high_interest="true")
    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "highInterest=true" in url


def test_announcements_list_is_get(api_client, respx_mock):
    # Fern calls _response.json() even for str return types; mock with json= not text=
    route = respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(200, json="")
    )
    api_client.bulk_data.announcements.list()
    assert route.called
    assert route.calls[0].request.method == "GET"


def test_announcements_list_optional_type_param(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/bulkdata/announcements").mock(
        return_value=httpx.Response(200, json="")
    )
    api_client.bulk_data.announcements.list(type="OPERATIONAL")
    url = str(route.calls[0].request.url)
    assert "type=OPERATIONAL" in url
