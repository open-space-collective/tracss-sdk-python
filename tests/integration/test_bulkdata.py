# Copyright © Loft Orbital Solutions Inc.
"""
Integration tests for the Bulk Data API.

Requires Prism in dynamic mode:
    prism mock -d fern/openapi/bulk_data/openapi.json --port 4011
Run via: make integration
"""

import pytest

from tracss.bulk_data.cdm.types import StreamCdmResponse
from tracss.bulk_data.ocm.types import StreamOcmResponse
from tracss.core import RequestOptions


@pytest.mark.integration
class TestBulkDataCdm:
    def test_stream_method_callable(self, bulkdata_client):
        assert callable(bulkdata_client.bulk_data.cdm.stream)

    def test_stream_no_args(self, ndjson_client):
        chunks = list(
            ndjson_client.bulk_data.cdm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        )
        assert all(isinstance(c, StreamCdmResponse) for c in chunks)

    def test_stream_with_filters(self, ndjson_client):
        chunks = list(
            ndjson_client.bulk_data.cdm.stream(
                tca=">2024-01-01T00:00:00Z",
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                ),
            )
        )
        assert all(isinstance(c, StreamCdmResponse) for c in chunks)

    def test_stream_v1_method_callable(self, bulkdata_client):
        assert callable(bulkdata_client.bulk_data.cdm.stream_v1)


@pytest.mark.integration
class TestBulkDataOcm:
    def test_stream_method_callable(self, bulkdata_client):
        assert callable(bulkdata_client.bulk_data.ocm.stream)

    def test_stream_no_args(self, ndjson_client):
        chunks = list(
            ndjson_client.bulk_data.ocm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        )
        assert all(isinstance(c, StreamOcmResponse) for c in chunks)

    def test_stream_v1_method_callable(self, bulkdata_client):
        assert callable(bulkdata_client.bulk_data.ocm.stream_v1)


@pytest.mark.integration
class TestBulkDataTip:
    def test_stream_method_callable(self, bulkdata_client):
        assert callable(bulkdata_client.bulk_data.tip.stream)

    def test_stream_no_args(self, bulkdata_client):
        result = bulkdata_client.bulk_data.tip.stream(
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            )
        )
        assert result is not None


@pytest.mark.integration
class TestBulkDataAnnouncements:
    def test_list_method_callable(self, bulkdata_client):
        assert callable(bulkdata_client.bulk_data.announcements.list)

    @pytest.mark.xfail(
        reason="Prism returns 406 for */* endpoints with Accept: application/json",
        strict=False,
    )
    def test_list_returns(self, bulkdata_client):
        result = bulkdata_client.bulk_data.announcements.list(
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            )
        )
        assert result is not None


@pytest.mark.integration
class TestBulkDataAsync:
    async def test_cdm_stream_async(self, async_ndjson_client):
        chunks = [
            c
            async for c in async_ndjson_client.bulk_data.cdm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        ]
        assert all(isinstance(c, StreamCdmResponse) for c in chunks)

    async def test_ocm_stream_async(self, async_ndjson_client):
        chunks = [
            c
            async for c in async_ndjson_client.bulk_data.ocm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        ]
        assert all(isinstance(c, StreamOcmResponse) for c in chunks)
