# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Metadata API client surface."""

import io
from http import HTTPStatus

import httpx
import pytest
import respx

BASE = "https://api.tracss.gov"


# ── Contact Directory ──────────────────────────────────────────────────────────


def test_contact_directory_list_operational_path(api_client, respx_mock):
    """Override must place this under contact_directory, not operator_controller."""
    route = respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )
    api_client.metadata.contact_directory.list_operational()
    assert route.called


def test_contact_directory_list_operational_returns_list(api_client, respx_mock):
    """Regression: metadata override pins list_operational return type.

    The override in fern/sdks/metadata-overrides.yaml pins the response type to
    List[OperationalContactInfoDto]. This test catches any regeneration that loses
    that override and falls back to a raw response or wrong type.
    """
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
    result = api_client.metadata.contact_directory.list_operational()
    assert isinstance(result, list), "list_operational must return a list"
    assert len(result) == 1
    from tracss.metadata.types import OperationalContactInfoDto

    assert isinstance(result[0], OperationalContactInfoDto)


def test_contact_directory_list_operational_optional_filters(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(HTTPStatus.OK, json=[])
    )
    api_client.metadata.contact_directory.list_operational(
        norad_id="12345", organization="Acme"
    )
    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "organization=Acme" in url


def test_contact_directory_update_operational_is_put(api_client, respx_mock):
    route = respx_mock.put(f"{BASE}/metadata/contactDirectory/operational/update").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.contact_directory.update_operational(request={"name": "John"})
    assert route.calls[0].request.method == "PUT"


# ── OCM ───────────────────────────────────────────────────────────────────────


def test_ocm_list_uses_v2_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.ocm.list()
    assert route.called


def test_ocm_list_v1_uses_legacy_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.ocm.list_v1()
    assert route.called


def test_ocm_upload_is_post_to_v2(api_client, respx_mock):
    route = respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.ocm.upload(
        file=("test.xml", io.BytesIO(b"<ocm/>"), "application/xml")
    )
    assert route.calls[0].request.method == "POST"


def test_ocm_upload_v1_is_post_to_legacy_path(api_client, respx_mock):
    route = respx_mock.post(f"{BASE}/metadata/ocm/upload").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.ocm.upload_v1(
        file=("test.xml", io.BytesIO(b"<ocm/>"), "application/xml")
    )
    assert route.calls[0].request.method == "POST"


def test_ocm_list_by_operational_batch_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm/operationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.ocm.list_by_operational_batch()
    assert route.called


# ── CDM ───────────────────────────────────────────────────────────────────────


def test_cdm_list_uses_v2_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.cdm.list()
    assert route.called


def test_cdm_list_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.cdm.list(
        tca=">2024-01-01", message_for="SAT-1", miss_distance="<500"
    )
    url = str(route.calls[0].request.url)
    assert "tca=" in url
    assert "messageFor=" in url
    assert "missDistance=" in url


def test_cdm_list_v1_uses_legacy_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.cdm.list_v1()
    assert route.called


def test_cdm_list_by_operational_batch_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdmByOperationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.cdm.list_by_operational_batch(batch_id="test-batch-001")
    assert route.called


def test_cdm_list_by_operational_batch_v1_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tracssCdmByOperationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.cdm.list_by_operational_batch_v1(batch_id="test-batch-001")
    assert route.called


def test_cdm_list_sends_json_format_by_default(api_client, respx_mock):
    """CDM list must send format=json when the caller omits format.

    The TraCSS API returns text/plain (KVN) when format is absent; the generated
    response parser cannot handle non-JSON bodies. _JsonCdmClient injects the default.
    """
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.cdm.list()
    assert "format=json" in str(route.calls[0].request.url)


def test_cdm_list_respects_explicit_format(api_client, respx_mock):
    """Explicit format= must not be overridden by the json default.

    Verifies setdefault semantics: XML (a non-JSON spec format) is forwarded
    unchanged to the server and the raw body is returned as str.
    """
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, text="<cdm/>")
    )
    result = api_client.metadata.cdm.list(format="xml")
    assert "format=xml" in str(route.calls[0].request.url)
    assert isinstance(result, str)


def test_ocm_list_sends_json_format_by_default(api_client, respx_mock):
    """OCM list must send format=json when the caller omits format."""
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.ocm.list()
    assert "format=json" in str(route.calls[0].request.url)


def test_cdm_list_returns_raw_str_for_kvn_format(api_client, respx_mock):
    """Explicit format='KVN' must return raw body str and forward format to server."""
    kvn = "CCSDS_CDM_VERS = 1.0\r\nCREATION_DATE = 2024-01-01"
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=kvn)
    )
    result = api_client.metadata.cdm.list(format="KVN")
    assert "format=KVN" in str(route.calls[0].request.url)
    assert isinstance(result, str)
    assert "CCSDS_CDM_VERS" in result


def test_cdm_list_returns_raw_str_for_csv_format(api_client, respx_mock):
    """format='csv' (CDM-only spec format) must return raw body str."""
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(
            HTTPStatus.OK, text="TCA,MISS_DISTANCE\n2024-01-01,500"
        )
    )
    result = api_client.metadata.cdm.list(format="csv")
    assert "format=csv" in str(route.calls[0].request.url)
    assert isinstance(result, str)


def test_ocm_list_returns_raw_str_for_kvn_format(api_client, respx_mock):
    """Explicit format='KVN' on OCM must return raw body str and forward format."""
    kvn = "CCSDS_OCM_VERS = 3.0\r\nCREATION_DATE = 2024-01-01"
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=kvn)
    )
    result = api_client.metadata.ocm.list(format="KVN")
    assert "format=KVN" in str(route.calls[0].request.url)
    assert isinstance(result, str)
    assert "CCSDS_OCM_VERS" in result


def test_cdm_list_propagates_non_200_api_error(api_client, respx_mock):
    """Non-200 ApiErrors (4xx, 5xx) must not be swallowed by the wrapper."""
    from tracss.core.api_error import ApiError

    respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN, json={"error": "forbidden"})
    )
    with pytest.raises(ApiError) as exc_info:
        api_client.metadata.cdm.list()
    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


# ── Async CDM / OCM (format defaulting) ──────────────────────────────────────


@pytest.mark.asyncio
async def test_async_cdm_list_sends_json_format_by_default(async_api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.cdm.list()
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_cdm_list_by_operational_batch_sends_json_format_by_default(
    async_api_client, respx_mock
):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdmByOperationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.cdm.list_by_operational_batch(batch_id="b1")
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_cdm_list_v1_sends_json_format_by_default(
    async_api_client, respx_mock
):
    route = respx_mock.get(f"{BASE}/metadata/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.cdm.list_v1()
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_cdm_list_by_operational_batch_v1_sends_json_format_by_default(
    async_api_client, respx_mock
):
    route = respx_mock.get(f"{BASE}/metadata/tracssCdmByOperationalBatch").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.cdm.list_by_operational_batch_v1(batch_id="b1")
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_ocm_list_sends_json_format_by_default(async_api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.ocm.list()
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_ocm_list_v1_sends_json_format_by_default(
    async_api_client, respx_mock
):
    route = respx_mock.get(f"{BASE}/metadata/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.ocm.list_v1()
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_cdm_list_returns_raw_str_for_kvn_format(
    async_api_client, respx_mock
):
    """Async CDM list with format='KVN' must return raw body str."""
    kvn = "CCSDS_CDM_VERS = 1.0\r\nCREATION_DATE = 2024-01-01"
    respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=kvn)
    )
    result = await async_api_client.metadata.cdm.list(format="KVN")
    assert isinstance(result, str)
    assert "CCSDS_CDM_VERS" in result


@pytest.mark.asyncio
async def test_async_ocm_list_returns_raw_str_for_kvn_format(
    async_api_client, respx_mock
):
    """Async OCM list with format='KVN' must return raw body str."""
    kvn = "CCSDS_OCM_VERS = 3.0\r\nCREATION_DATE = 2024-01-01"
    respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=kvn)
    )
    result = await async_api_client.metadata.ocm.list(format="KVN")
    assert isinstance(result, str)
    assert "CCSDS_OCM_VERS" in result


@pytest.mark.asyncio
async def test_async_cdm_list_propagates_non_200_api_error(async_api_client, respx_mock):
    """Non-200 ApiErrors must not be swallowed by the async wrapper."""
    from tracss.core.api_error import ApiError

    respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN, json={"error": "forbidden"})
    )
    with pytest.raises(ApiError) as exc_info:
        await async_api_client.metadata.cdm.list()
    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


# ── Metadata subclass regression guards ───────────────────────────────────────


def test_metadata_property_returns_json_defaults_subclass(api_client):
    from tracss.client import _MetadataWithJsonDefaults

    assert isinstance(api_client.metadata, _MetadataWithJsonDefaults)


@pytest.mark.asyncio
async def test_async_metadata_property_returns_json_defaults_subclass(async_api_client):
    from tracss.client import _AsyncMetadataWithJsonDefaults

    assert isinstance(async_api_client.metadata, _AsyncMetadataWithJsonDefaults)


def test_metadata_tip_reports_returns_json_defaults_subclass(api_client):
    from tracss.client import _JsonTipReportsClient

    assert isinstance(api_client.metadata.tip_reports, _JsonTipReportsClient)


@pytest.mark.asyncio
async def test_async_metadata_tip_reports_returns_json_defaults_subclass(
    async_api_client,
):
    from tracss.client import _AsyncJsonTipReportsClient

    assert isinstance(async_api_client.metadata.tip_reports, _AsyncJsonTipReportsClient)


# ── TraCSS CAT ────────────────────────────────────────────────────────────────


def test_tracss_cat_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.tracss_cat.list()
    assert route.called


def test_tracss_cat_list_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.tracss_cat.list(norad_id="12345", organization="Acme")
    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "organization=Acme" in url


def test_tracss_cat_upload_csv_is_post(api_client, respx_mock):
    route = respx_mock.post(f"{BASE}/metadata/tracssCat/update/csv").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.tracss_cat.upload_csv()
    assert route.calls[0].request.method == "POST"


# ── Other Namespaces ──────────────────────────────────────────────────────────


def test_tip_reports_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.tip_reports.list()
    assert route.called


def test_tip_reports_list_sends_json_format_by_default(api_client, respx_mock):
    """TIP report list must send format=json when the caller omits format.

    The TraCSS API returns text/plain (KVN) when format is absent; the generated
    response parser cannot handle non-JSON bodies. _JsonTipReportsClient injects it.
    """
    route = respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.tip_reports.list()
    assert "format=json" in str(route.calls[0].request.url)


def test_tip_reports_list_returns_raw_str_for_kvn_format(api_client, respx_mock):
    """Explicit format='KVN' must return raw body str and forward format to server."""
    kvn = "CCSDS_TIP_VERS = 1.0\r\nCREATION_DATE = 2024-01-01"
    route = respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=kvn)
    )
    result = api_client.metadata.tip_reports.list(format="KVN")
    assert "format=KVN" in str(route.calls[0].request.url)
    assert isinstance(result, str)
    assert "CCSDS_TIP_VERS" in result


def test_tip_reports_list_returns_raw_str_for_xml_format(api_client, respx_mock):
    """Explicit format='xml' must return raw body str."""
    route = respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.OK, text="<tipReport/>")
    )
    result = api_client.metadata.tip_reports.list(format="xml")
    assert "format=xml" in str(route.calls[0].request.url)
    assert isinstance(result, str)


def test_tip_reports_list_propagates_non_200_api_error(api_client, respx_mock):
    """Non-200 ApiErrors (4xx, 5xx) must not be swallowed by the TipReports wrapper."""
    from tracss.core.api_error import ApiError

    respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN, json={"error": "forbidden"})
    )
    with pytest.raises(ApiError) as exc_info:
        api_client.metadata.tip_reports.list()
    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_async_tip_reports_list_sends_json_format_by_default(
    async_api_client, respx_mock
):
    route = respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    await async_api_client.metadata.tip_reports.list()
    assert "format=json" in str(route.calls[0].request.url)


@pytest.mark.asyncio
async def test_async_tip_reports_list_returns_raw_str_for_kvn_format(
    async_api_client, respx_mock
):
    """Async TIP report list with format='KVN' must return raw body str."""
    kvn = "CCSDS_TIP_VERS = 1.0\r\nCREATION_DATE = 2024-01-01"
    respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.OK, text=kvn)
    )
    result = await async_api_client.metadata.tip_reports.list(format="KVN")
    assert isinstance(result, str)
    assert "CCSDS_TIP_VERS" in result


@pytest.mark.asyncio
async def test_async_tip_reports_list_propagates_non_200_api_error(
    async_api_client, respx_mock
):
    """Non-200 ApiErrors must not be swallowed by the async TipReports wrapper."""
    from tracss.core.api_error import ApiError

    respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN, json={"error": "forbidden"})
    )
    with pytest.raises(ApiError) as exc_info:
        await async_api_client.metadata.tip_reports.list()
    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


def test_conjunction_events_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.conjunction_events.list()
    assert route.called


def test_announcements_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/announcements").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.announcements.list()
    assert route.called


def test_schemas_get_xsd_path(api_client, respx_mock):
    # Returns List[str] (URLs); Fern calls _response.json(), so use json= not text=
    route = respx_mock.get(f"{BASE}/metadata/schemas/xsd").mock(
        return_value=httpx.Response(
            200, json=["https://api.tracss.gov/metadata/schemas/cdm.xsd"]
        )
    )
    api_client.metadata.schemas.get_xsd()
    assert route.called


def test_schemas_get_json_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/schemas/json").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.metadata.schemas.get_json()
    assert route.called
