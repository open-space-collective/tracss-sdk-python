# Copyright © Loft Orbital Solutions Inc.
"""
Integration tests for the Subscriber API.

Requires Prism mock servers running (start with: make prism-all):
  prism mock fern/openapi/subscriber/openapi.json --port 4010

Run via: make integration
"""

import pytest


@pytest.mark.integration
class TestSubscriberTopics:
    def test_list_method_callable(self, subscriber_client):
        assert callable(subscriber_client.subscriber.topics.list)

    def test_list_returns(self, subscriber_client):
        result = subscriber_client.subscriber.topics.list()
        assert result is not None

    def test_get_offset_method_callable(self, subscriber_client):
        assert callable(subscriber_client.subscriber.topics.get_offset)

    def test_get_offset_with_topic(self, subscriber_client):
        result = subscriber_client.subscriber.topics.get_offset(
            topic="gov.tracss.tracss.v1.cdms"
        )
        assert result is not None


@pytest.mark.integration
class TestSubscriberMessages:
    def test_list_method_callable(self, subscriber_client):
        assert callable(subscriber_client.subscriber.messages.list)

    def test_list_minimal_args(self, subscriber_client):
        result = subscriber_client.subscriber.messages.list(
            topic="gov.tracss.tracss.v1.cdms", offset="0"
        )
        assert result is not None

    def test_list_with_max_results(self, subscriber_client):
        result = subscriber_client.subscriber.messages.list(
            topic="gov.tracss.tracss.v1.cdms", offset="0", max_results="10"
        )
        assert result is not None


@pytest.mark.integration
class TestSubscriberAsync:
    async def test_topics_list_async(self, async_subscriber_client):
        result = await async_subscriber_client.subscriber.topics.list()
        assert result is not None

    async def test_messages_list_async(self, async_subscriber_client):
        result = await async_subscriber_client.subscriber.messages.list(
            topic="gov.tracss.tracss.v1.cdms", offset="0"
        )
        assert result is not None
