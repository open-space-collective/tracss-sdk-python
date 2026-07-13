# SPDX-License-Identifier: Apache-2.0
"""Integration tests for the Metadata API.

Requires Prism: prism mock fern/openapi/metadata/openapi.json --port 4012
Run via: make integration
"""

import pytest

from tracss.metadata.cdm.types import ListByOperationalBatchCdmResponse, ListCdmResponse
from tracss.metadata.ocm.types import ListOcmResponse
from tracss.metadata.types import OperationalContactInfoDto, Operator


@pytest.mark.integration
class TestMetadataContactDirectory:
    """Integration tests for metadata.contact_directory endpoints."""

    @pytest.mark.xfail(
        reason=(
            "Prism serves the underspecified `type: object` response as a "
            "named-examples map; the SDK contract and live API return "
            "List[OperationalContactInfoDto]. Prism-only."
        ),
        strict=True,
    )
    def test_list_operational_returns(self, metadata_client):
        result = metadata_client.metadata.contact_directory.list_operational()
        assert isinstance(result, list)
        assert all(isinstance(item, OperationalContactInfoDto) for item in result)

    def test_update_operational_sends_put(self, metadata_client):
        # noradIds is a required query parameter on this endpoint (per the spec).
        result = metadata_client.metadata.contact_directory.update_operational(
            norad_ids=["12345"],
            request={"name": "Test Operator"},
        )
        assert isinstance(result, Operator)


@pytest.mark.integration
class TestMetadataOcm:
    """Integration tests for metadata.ocm endpoints."""

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.ocm.list()
        assert isinstance(result, ListOcmResponse)

    def test_upload_sends_request(self, metadata_client):
        import io

        result = metadata_client.metadata.ocm.upload(
            file=("test.xml", io.BytesIO(b"<ocm/>"), "application/xml")
        )
        assert isinstance(result, (dict, str)), (
            f"Expected dict (JSON 201) or str (text/plain 201), "
            f"got {type(result).__name__}"
        )


@pytest.mark.integration
class TestMetadataCdm:
    """Integration tests for metadata.cdm endpoints."""

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.cdm.list()
        assert isinstance(result, ListCdmResponse)

    def test_list_returns_typed_response_not_raw(self, metadata_client):
        """format=json default must be applied - typed ListCdmResponse, never RawResponse.

        If _MetadataWithJsonDefaults stops wrapping the cdm property (e.g. a
        Fern generator bump renames the private _cdm attribute it overrides),
        the format=json default is silently lost and Prism returns KVN text.
        That causes ApiError(status_code=200) which _call_or_raw converts to
        RawResponse - caught here.
        """
        from tracss.client import RawResponse

        result = metadata_client.metadata.cdm.list()
        assert not isinstance(result, RawResponse), (
            "metadata.cdm.list() returned RawResponse instead of ListCdmResponse - "
            "the format=json default may not be reaching the server"
        )
        assert isinstance(result, ListCdmResponse)

    def test_list_by_operational_batch_returns(self, metadata_client):
        result = metadata_client.metadata.cdm.list_by_operational_batch(
            batch_id="test-batch-001"
        )
        assert isinstance(result, ListByOperationalBatchCdmResponse)


@pytest.mark.integration
class TestMetadataTracssCat:
    """Integration tests for metadata.tracss_cat endpoints."""

    @pytest.mark.xfail(
        reason=(
            "Prism serves the underspecified `type: object` response as a named-examples "
            "map; the SDK contract and live API return a JSON array. Prism-only."
        ),
        strict=True,
    )
    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.tracss_cat.list()
        assert isinstance(result, list)

    def test_upload_csv_sends_request(self, metadata_client):
        import io

        # A successful multipart upload returns 2xx; this endpoint's success body is
        # empty, so the parsed result is None. Reaching here without a raised typed
        # error confirms the CSV file field was accepted.
        result = metadata_client.metadata.tracss_cat.upload_csv(
            file=("test.csv", io.BytesIO(b"noradId\n12345\n"), "text/csv")
        )
        assert result is None or isinstance(result, (dict, list, str))


@pytest.mark.integration
class TestMetadataNewSubClients:
    """Connectivity tests for sub-clients added in the latest spec refresh.

    These endpoints have no format parameter and require no wrapper; the tests
    verify that Fern's generated method routing is correct after a generator
    upgrade (a rename of private attributes would silently break them).
    """

    def test_space_track_list_returns(self, metadata_client):
        result = metadata_client.metadata.space_track.list()
        assert isinstance(result, list)

    def test_space_track_list_nested_returns(self, metadata_client):
        result = metadata_client.metadata.space_track.list_nested()
        assert isinstance(result, list)

    @pytest.mark.xfail(
        reason=(
            "Prism cannot serialize the complex schema response as text/plain "
            "(NO_COMPLEX_OBJECT_TEXT 500); the live API returns the schema "
            "payload. Prism-only."
        ),
        strict=True,
    )
    def test_schemas_get_xsd_returns(self, metadata_client):
        result = metadata_client.metadata.schemas.get_xsd()
        assert isinstance(result, list)

    @pytest.mark.xfail(
        reason=(
            "Prism cannot serialize the complex schema response as text/plain "
            "(NO_COMPLEX_OBJECT_TEXT 500); the live API returns the schema "
            "payload. Prism-only."
        ),
        strict=True,
    )
    def test_schemas_get_json_returns(self, metadata_client):
        result = metadata_client.metadata.schemas.get_json()
        assert isinstance(result, list)

    def test_conjunction_events_list_returns(self, metadata_client):
        from tracss.metadata.conjunction_events.types import ListConjunctionEventsResponse

        result = metadata_client.metadata.conjunction_events.list()
        assert isinstance(result, ListConjunctionEventsResponse)

    def test_announcements_list_returns(self, metadata_client):
        result = metadata_client.metadata.announcements.list()
        assert isinstance(result, list)


@pytest.mark.integration
class TestMetadataAsync:
    """Async variants of the Metadata API integration tests."""

    async def test_cdm_list_async(self, async_metadata_client):
        result = await async_metadata_client.metadata.cdm.list()
        assert isinstance(result, ListCdmResponse)

    async def test_ocm_list_async(self, async_metadata_client):
        result = await async_metadata_client.metadata.ocm.list()
        assert isinstance(result, ListOcmResponse)
