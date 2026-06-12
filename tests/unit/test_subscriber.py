# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Subscriber API client surface."""

from http import HTTPStatus

import httpx
import pytest
import respx

BASE = "https://api.tracss.gov"


def test_topics_list_is_get(api_client, respx_mock):
    # Fern calls _response.json() even for str return types; mock with json= not text=
    route = respx_mock.get(f"{BASE}/subscriber/topics").mock(
        return_value=httpx.Response(
            200, json="gov.tracss.tracss.v1.cdms\ngov.tracss.tracss.v2.cdms"
        )
    )
    api_client.subscriber.topics.list()
    assert route.called
    assert route.calls[0].request.method == "GET"


def test_topics_list_no_required_params(api_client, respx_mock):
    respx_mock.get(f"{BASE}/subscriber/topics").mock(
        return_value=httpx.Response(HTTPStatus.OK, json="")
    )
    # Must not raise TypeError - no required params
    api_client.subscriber.topics.list()


def test_topics_get_offset_sends_topic(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/subscriber/offset").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"offset": 42})
    )
    api_client.subscriber.topics.get_offset(topic="gov.tracss.tracss.v2.cdms")
    url = str(route.calls[0].request.url)
    assert "topic=gov.tracss.tracss.v2.cdms" in url


def test_topics_get_offset_requires_topic(api_client, respx_mock):
    respx_mock.get(f"{BASE}/subscriber/offset").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    with pytest.raises(TypeError):
        api_client.subscriber.topics.get_offset()  # topic is required


def test_messages_list_minimal_args(api_client, respx_mock):
    route = respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.subscriber.messages.list(topic="gov.tracss.tracss.v2.cdms", offset="0")
    url = str(route.calls[0].request.url)
    assert "topic=gov.tracss.tracss.v2.cdms" in url
    assert "offset=0" in url
    assert "maxResults" not in url
    assert "filterDesignators" not in url
    assert "fields" not in url


def test_messages_list_full_args(api_client, respx_mock):
    respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    api_client.subscriber.messages.list(
        topic="gov.tracss.tracss.v2.cdms",
        offset="100",
        max_results="50",
        filter_designators="12345",
        fields="missDistance,collisionProbability",
    )
    url = str(respx_mock.calls[0].request.url)
    assert "maxResults=50" in url
    assert "filterDesignators=12345" in url
    assert "fields=missDistance" in url


def test_messages_list_requires_topic_and_offset(api_client, respx_mock):
    respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )
    with pytest.raises(TypeError):
        api_client.subscriber.messages.list()  # topic and offset are required


def test_messages_list_401_raises(api_client, respx_mock):
    respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(
            HTTPStatus.UNAUTHORIZED, json={"error": "unauthorized"}
        )
    )
    from tracss.subscriber.errors import UnauthorizedError

    with pytest.raises(UnauthorizedError):
        api_client.subscriber.messages.list(topic="t", offset="0")
