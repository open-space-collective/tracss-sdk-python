# SPDX-License-Identifier: Apache-2.0
"""Integration tests for the Metadata API.

Requires Prism: prism mock fern/openapi/metadata/openapi.json --port 4012
Run via: make integration
"""

import pytest


@pytest.mark.integration
class TestMetadataContactDirectory:
    """Integration tests for metadata.contact_directory endpoints."""

    def test_list_operational_callable(self, metadata_client):
        assert callable(metadata_client.metadata.contact_directory.list_operational)

    def test_list_operational_returns(self, metadata_client):
        result = metadata_client.metadata.contact_directory.list_operational()
        assert result is not None

    def test_update_operational_callable(self, metadata_client):
        assert callable(metadata_client.metadata.contact_directory.update_operational)


@pytest.mark.integration
class TestMetadataOcm:
    """Integration tests for metadata.ocm endpoints."""

    def test_list_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.list)

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.ocm.list()
        assert result is not None

    def test_list_v1_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.list_v1)

    def test_upload_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.upload)

    def test_upload_v1_callable(self, metadata_client):
        assert callable(metadata_client.metadata.ocm.upload_v1)


@pytest.mark.integration
class TestMetadataCdm:
    """Integration tests for metadata.cdm endpoints."""

    def test_list_callable(self, metadata_client):
        assert callable(metadata_client.metadata.cdm.list)

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.cdm.list()
        assert result is not None

    def test_list_v1_callable(self, metadata_client):
        assert callable(metadata_client.metadata.cdm.list_v1)

    def test_list_by_operational_batch_callable(self, metadata_client):
        assert callable(metadata_client.metadata.cdm.list_by_operational_batch)


@pytest.mark.integration
class TestMetadataTracssCat:
    """Integration tests for metadata.tracss_cat endpoints."""

    def test_list_callable(self, metadata_client):
        assert callable(metadata_client.metadata.tracss_cat.list)

    def test_list_returns(self, metadata_client):
        result = metadata_client.metadata.tracss_cat.list()
        assert result is not None

    def test_upload_csv_callable(self, metadata_client):
        assert callable(metadata_client.metadata.tracss_cat.upload_csv)


@pytest.mark.integration
class TestMetadataAsync:
    """Async variants of the Metadata API integration tests."""

    async def test_cdm_list_async(self, async_metadata_client):
        result = await async_metadata_client.metadata.cdm.list()
        assert result is not None

    async def test_ocm_list_async(self, async_metadata_client):
        result = await async_metadata_client.metadata.ocm.list()
        assert result is not None
