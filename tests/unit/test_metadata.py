# Copyright © Loft Orbital Solutions Inc.
import io

import httpx
import pytest
import respx

BASE = "https://api.tracss.gov"


# ── Contact Directory ──────────────────────────────────────────────────────────


def test_contact_directory_list_operational_path(api_client, respx_mock):
    """Override must place this under contact_directory, not operator_controller."""
    route = respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(200, json=[])
    )
    api_client.metadata.contact_directory.list_operational()
    assert route.called


def test_contact_directory_list_operational_returns_list(api_client, respx_mock):
    """
    Regression: override in fern/sdks/metadata-overrides.yaml pins the response
    type to List[OperationalContactInfoDto]. This test catches any regeneration
    that loses that override and falls back to a raw response or wrong type.
    """
    payload = [
        {
            "satelliteOwnershipGroup": "Acme Sat Co",
            "satellites": [{"noradId": 12345, "name": "ACME-1"}],
            "contacts": [{"name": "John Doe", "email": "john@acme.com"}],
        }
    ]
    respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(200, json=payload)
    )
    result = api_client.metadata.contact_directory.list_operational()
    assert isinstance(result, list), "list_operational must return a list"
    assert len(result) == 1
    from tracss.metadata.types import OperationalContactInfoDto

    assert isinstance(result[0], OperationalContactInfoDto)


def test_contact_directory_list_operational_optional_filters(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/contactDirectory/operational/all").mock(
        return_value=httpx.Response(200, json=[])
    )
    api_client.metadata.contact_directory.list_operational(
        norad_id="12345", organization="Acme"
    )
    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "organization=Acme" in url


def test_contact_directory_update_operational_is_put(api_client, respx_mock):
    route = respx_mock.put(f"{BASE}/metadata/contactDirectory/operational/update").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.contact_directory.update_operational(request={"name": "John"})
    assert route.calls[0].request.method == "PUT"


# ── OCM ───────────────────────────────────────────────────────────────────────


def test_ocm_list_uses_v2_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.ocm.list()
    assert route.called


def test_ocm_list_v1_uses_legacy_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/ocm").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.ocm.list_v1()
    assert route.called


def test_ocm_upload_is_post_to_v2(api_client, respx_mock):
    route = respx_mock.post(f"{BASE}/metadata/v2/ocm/upload").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.ocm.upload(
        file=("test.xml", io.BytesIO(b"<ocm/>"), "application/xml")
    )
    assert route.calls[0].request.method == "POST"


def test_ocm_upload_v1_is_post_to_legacy_path(api_client, respx_mock):
    route = respx_mock.post(f"{BASE}/metadata/ocm/upload").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.ocm.upload_v1(
        file=("test.xml", io.BytesIO(b"<ocm/>"), "application/xml")
    )
    assert route.calls[0].request.method == "POST"


def test_ocm_list_by_operational_batch_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/ocm/operationalBatch").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.ocm.list_by_operational_batch()
    assert route.called


# ── CDM ───────────────────────────────────────────────────────────────────────


def test_cdm_list_uses_v2_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.cdm.list()
    assert route.called


def test_cdm_list_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdm").mock(
        return_value=httpx.Response(200, json={})
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
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.cdm.list_v1()
    assert route.called


def test_cdm_list_by_operational_batch_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/v2/tracssCdmByOperationalBatch").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.cdm.list_by_operational_batch(batch_id="test-batch-001")
    assert route.called


# ── TraCSS CAT ────────────────────────────────────────────────────────────────


def test_tracss_cat_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.tracss_cat.list()
    assert route.called


def test_tracss_cat_list_partial_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tracssCat").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.tracss_cat.list(norad_id="12345", organization="Acme")
    url = str(route.calls[0].request.url)
    assert "noradId=12345" in url
    assert "organization=Acme" in url


def test_tracss_cat_upload_csv_is_post(api_client, respx_mock):
    route = respx_mock.post(f"{BASE}/metadata/tracssCat/update/csv").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.tracss_cat.upload_csv()
    assert route.calls[0].request.method == "POST"


# ── Other Namespaces ──────────────────────────────────────────────────────────


def test_tip_reports_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/tipReports").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.tip_reports.list()
    assert route.called


def test_conjunction_events_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/conjunctionDataEvents").mock(
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.conjunction_events.list()
    assert route.called


def test_announcements_list_path(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/metadata/announcements").mock(
        return_value=httpx.Response(200, json={})
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
        return_value=httpx.Response(200, json={})
    )
    api_client.metadata.schemas.get_json()
    assert route.called
