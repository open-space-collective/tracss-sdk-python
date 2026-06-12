# Copyright © Loft Orbital Solutions Inc.
"""
Integration tests for the Metadata API.

Requires Prism: prism mock fern/openapi/metadata/openapi.json --port 4012
Run via: make integration
"""

import pytest

from tracss.core import RequestOptions


@pytest.mark.integration
class TestMetadataContactDirectory:
    def test_list_operational_callable(self, metadata_client):
        assert callable(metadata_client.metadata.contact_directory.list_operational)

    def test_list_operational_returns(self, metadata_client):
        result = metadata_client.metadata.contact_directory.list_operational()
        assert result is not None

    def test_update_operational_callable(self, metadata_client):
        assert callable(metadata_client.metadata.contact_directory.update_operational)


@pytest.mark.integration
class TestMetadataOcm:
    def test_list_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.list)

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.ocm.list(
            format="json",
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            ),
        )
        assert result is not None

    def test_list_v1_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.list_v1)

    def test_upload_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.upload)

    def test_upload_v1_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.upload_v1)


@pytest.mark.integration
class TestMetadataCdm:
    def test_list_callable(self, metadata_client):
        assert callable(metadata_client.metadata.cdm.list)

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.cdm.list(
            format="json",
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            ),
        )
        assert result is not None

    def test_list_v1_callable(self, metadata_client):
        assert callable(metadata_client.metadata.cdm.list_v1)

    def test_list_by_operational_batch_callable(self, metadata_client):
        assert callable(metadata_client.metadata.cdm.list_by_operational_batch)


@pytest.mark.integration
class TestMetadataTracssCat:
    def test_list_callable(self, metadata_client):
        assert callable(metadata_client.metadata.tracss_cat.list)

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.tracss_cat.list()
        assert result is not None

    def test_upload_csv_callable(self, metadata_client):
        assert callable(metadata_client.metadata.tracss_cat.upload_csv)


@pytest.mark.integration
class TestMetadataAsync:
    async def test_cdm_list_async(self, async_metadata_client):
        result = await async_metadata_client.metadata.cdm.list(
            format="json",
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            ),
        )
        assert result is not None

    async def test_ocm_list_async(self, async_metadata_client):
        result = await async_metadata_client.metadata.ocm.list(
            format="json",
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            ),
        )
        assert result is not None
