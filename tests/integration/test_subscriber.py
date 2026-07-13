# SPDX-License-Identifier: Apache-2.0
"""Integration tests for the Subscriber API.

Requires Prism mock servers running (start with: make prism-all):
  prism mock fern/openapi/subscriber/openapi.json --port 4010

Run via: make integration
"""

import pytest

from tracss.subscriber.messages.types import ListMessagesResponse


@pytest.mark.integration
class TestSubscriberTopics:
    """Integration tests for subscriber.topics endpoints."""

    @pytest.mark.xfail(
        # Prism generates a JSON object for type:string endpoints; real API returns str
        reason="Prism/real-API content-type mismatch for string topics response",
        strict=True,
    )
    def test_list_returns(self, subscriber_client):
        result = subscriber_client.subscriber.topics.list()
        assert isinstance(result, str)

    def test_get_offset_with_topic(self, subscriber_client):
        result = subscriber_client.subscriber.topics.get_offset(
            topic="gov.tracss.tracss.v1.cdms"
        )
        assert isinstance(result, int)


@pytest.mark.integration
class TestSubscriberMessages:
    """Integration tests for subscriber.messages endpoints."""

    def test_list_minimal_args(self, subscriber_client):
        result = subscriber_client.subscriber.messages.list(
            topic="gov.tracss.tracss.v1.cdms", offset="0"
        )
        assert isinstance(result, ListMessagesResponse)

    def test_list_with_max_results(self, subscriber_client):
        result = subscriber_client.subscriber.messages.list(
            topic="gov.tracss.tracss.v1.cdms", offset="0", max_results="10"
        )
        assert isinstance(result, ListMessagesResponse)


@pytest.mark.integration
class TestSubscriberAsync:
    """Async variants of the Subscriber API integration tests."""

    @pytest.mark.xfail(
        # Prism generates a JSON object for type:string endpoints; real API returns str
        reason="Prism/real-API content-type mismatch for string topics response",
        strict=True,
    )
    async def test_topics_list_async(self, async_subscriber_client):
        result = await async_subscriber_client.subscriber.topics.list()
        assert isinstance(result, str)

    async def test_messages_list_async(self, async_subscriber_client):
        result = await async_subscriber_client.subscriber.messages.list(
            topic="gov.tracss.tracss.v1.cdms", offset="0"
        )
        assert isinstance(result, ListMessagesResponse)
