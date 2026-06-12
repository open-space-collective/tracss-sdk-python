# Copyright © Loft Orbital Solutions Inc.
"""
Smoke tests against the live TraCSS API.

These tests require real credentials in the environment:
  export TRACSS_CLIENT_ID=...
  export TRACSS_CLIENT_SECRET=...

Run via: make smoke
"""

import pytest


@pytest.mark.smoke
def test_subscriber_topics_list(live_client):
    result = live_client.subscriber.topics.list()
    assert result is not None


@pytest.mark.smoke
def test_metadata_cdm_list(live_client):
    result = live_client.metadata.cdm.list()
    assert result is not None


@pytest.mark.smoke
def test_bulkdata_cdm_stream(live_client):
    # May require elevated permissions; skip if a 403 is returned.
    result = live_client.bulk_data.cdm.stream()
    assert result is not None
