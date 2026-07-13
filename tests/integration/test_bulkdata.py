# SPDX-License-Identifier: Apache-2.0
"""Integration tests for the Bulk Data API.

Requires Prism in dynamic mode:
    prism mock -d fern/openapi/bulk_data/openapi.json --port 4011
Run via: make integration
"""

import json

import pytest

from tests.integration.conftest import (
    _CDM_HEADERS_EXAMPLE,
    _OCM_HEADERS_EXAMPLE,
    _TIP_KEYS_EXAMPLE,
)
from tracss.bulk_data.cdm.types import StreamCdmResponse
from tracss.bulk_data.ocm.types import StreamOcmResponse
from tracss.core import RequestOptions


@pytest.mark.integration
class TestBulkDataCdm:
    """Integration tests for bulk_data.cdm streaming endpoints."""

    def test_stream_no_args(self, ndjson_client):
        chunks = list(
            ndjson_client.bulk_data.cdm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        )
        assert len(chunks) == 1
        item = chunks[0]
        assert isinstance(item, StreamCdmResponse)
        # headers_only is Optional[str] - the API serializes the header object
        # as a JSON string.  Non-null + parseable guards against field renames:
        # if headersOnly is renamed in the spec+SDK, item.headers_only is None.
        assert item.headers_only is not None
        parsed = json.loads(item.headers_only)
        assert set(_CDM_HEADERS_EXAMPLE) <= set(parsed)

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


@pytest.mark.integration
class TestBulkDataOcm:
    """Integration tests for bulk_data.ocm streaming endpoints."""

    def test_stream_no_args(self, ndjson_client):
        chunks = list(
            ndjson_client.bulk_data.ocm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        )
        assert len(chunks) == 1
        item = chunks[0]
        assert isinstance(item, StreamOcmResponse)
        assert item.headers_only is not None
        parsed = json.loads(item.headers_only)
        assert set(_OCM_HEADERS_EXAMPLE) <= set(parsed)


@pytest.mark.integration
class TestBulkDataTip:
    """Integration tests for bulk_data.tip streaming endpoints."""

    def test_stream_no_args(self, ndjson_client):
        chunks = list(ndjson_client.bulk_data.tip.stream())
        assert len(chunks) == 1
        item = chunks[0]
        assert isinstance(item, dict)
        assert set(_TIP_KEYS_EXAMPLE) <= set(item)


@pytest.mark.integration
class TestBulkDataAnnouncements:
    """Integration tests for bulk_data.announcements endpoints."""

    @pytest.mark.xfail(
        reason=(
            "Prism serves the */* announcements response as a text/plain body 'string' "
            "(the literal example), which is not valid JSON; the live API returns a JSON "
            "array. Prism-only."
        ),
        strict=True,
    )
    def test_list_returns(self, bulkdata_client):
        result = bulkdata_client.bulk_data.announcements.list()
        assert isinstance(result, list)

    @pytest.mark.xfail(
        reason="Prism returns 406 for */* endpoints with Accept: application/json",
        strict=True,
    )
    def test_list_with_explicit_json_accept_rejected_by_prism(self, bulkdata_client):
        """Documents that Prism rejects Accept: application/json on */* endpoints.

        The live API is more lenient. This failure is Prism-only. The SDK default
        (no explicit Accept override) uses the endpoint correctly; see test_list_returns.
        """
        result = bulkdata_client.bulk_data.announcements.list(
            request_options=RequestOptions(
                additional_headers={"Accept": "application/json"}
            )
        )
        assert result is not None


@pytest.mark.integration
class TestBulkDataAsync:
    """Async variants of the Bulk Data streaming integration tests."""

    async def test_cdm_stream_async(self, async_ndjson_client):
        chunks = [
            c
            async for c in async_ndjson_client.bulk_data.cdm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        ]
        assert len(chunks) == 1
        item = chunks[0]
        assert isinstance(item, StreamCdmResponse)
        assert item.headers_only is not None
        assert set(_CDM_HEADERS_EXAMPLE) <= set(json.loads(item.headers_only))

    async def test_ocm_stream_async(self, async_ndjson_client):
        chunks = [
            c
            async for c in async_ndjson_client.bulk_data.ocm.stream(
                request_options=RequestOptions(
                    additional_headers={"Accept": "application/x-ndjson"}
                )
            )
        ]
        assert len(chunks) == 1
        item = chunks[0]
        assert isinstance(item, StreamOcmResponse)
        assert item.headers_only is not None
        assert set(_OCM_HEADERS_EXAMPLE) <= set(json.loads(item.headers_only))

    async def test_tip_stream_async(self, async_ndjson_client):
        chunks = [c async for c in async_ndjson_client.bulk_data.tip.stream()]
        assert len(chunks) == 1
        item = chunks[0]
        assert isinstance(item, dict)
        assert set(_TIP_KEYS_EXAMPLE) <= set(item)
