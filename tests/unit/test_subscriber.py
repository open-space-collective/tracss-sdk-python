# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Subscriber API client surface (``client.subscriber.*``).

Covers the generated `topics` and `messages` sub-clients plus the hand-written
`_JsonMessagesClient`/`_SubscriberWithMessages` 204-handling wrapper in
`tracss.client`. Low-level `_call_or_raw`-style mechanics are unit-tested in
`test_client.py`; this file proves the wrapper is actually wired in when
called through the public client.
"""

from http import HTTPStatus

import httpx
import pytest
import respx

from tests.conftest import maybe_await
from tracss.subscriber.errors import (
    BadGatewayError,
    BadRequestError,
    ExpectationFailedError,
    ForbiddenError,
    InternalServerError,
    MethodNotAllowedError,
    NotFoundError,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnauthorizedError,
)
from tracss.subscriber.messages.types.list_messages_response import (
    ListMessagesResponse,
)

BASE = "https://api.tracss.gov"

# (status_code, expected exception class) for every status code that
# subscriber/topics and subscriber/messages raw clients map explicitly.
STATUS_TO_ERROR = [
    (HTTPStatus.BAD_REQUEST, BadRequestError),
    (HTTPStatus.UNAUTHORIZED, UnauthorizedError),
    (HTTPStatus.FORBIDDEN, ForbiddenError),
    (HTTPStatus.NOT_FOUND, NotFoundError),
    (HTTPStatus.METHOD_NOT_ALLOWED, MethodNotAllowedError),
    (HTTPStatus.EXPECTATION_FAILED, ExpectationFailedError),
    (HTTPStatus.TOO_MANY_REQUESTS, TooManyRequestsError),
    (HTTPStatus.INTERNAL_SERVER_ERROR, InternalServerError),
    (HTTPStatus.BAD_GATEWAY, BadGatewayError),
    (HTTPStatus.SERVICE_UNAVAILABLE, ServiceUnavailableError),
]
STATUS_TO_ERROR_IDS = [cls.__name__ for _, cls in STATUS_TO_ERROR]
parametrize_status_to_error = pytest.mark.parametrize(
    ("status_code", "error_cls"), STATUS_TO_ERROR, ids=STATUS_TO_ERROR_IDS
)


# ── topics.list ────────────────────────────────────────────────────────────


async def test_topics_list_is_get(client_kind, respx_mock):
    """topics.list() issues a GET with no required params."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/topics").mock(
        return_value=httpx.Response(
            HTTPStatus.OK, json="gov.tracss.tracss.v1.cdms\ngov.tracss.tracss.v2.cdms"
        )
    )

    # Act
    result = await maybe_await(client_kind.subscriber.topics.list())

    # Assert
    assert route.calls[0].request.method == "GET"
    assert result == "gov.tracss.tracss.v1.cdms\ngov.tracss.tracss.v2.cdms"


@parametrize_status_to_error
async def test_topics_list_maps_status_to_exception(
    client_kind, respx_mock, status_code, error_cls
):
    """Each mapped status code on subscriber/topics raises its dedicated exception."""
    # Arrange
    body = {"error": "detail"}
    respx_mock.get(f"{BASE}/subscriber/topics").mock(
        return_value=httpx.Response(status_code, json=body)
    )

    # Act / Assert
    with pytest.raises(error_cls) as exc_info:
        await maybe_await(client_kind.subscriber.topics.list())
    assert exc_info.value.status_code == status_code
    assert exc_info.value.body == body


# ── topics.get_offset ────────────────────────────────────────────────────────


async def test_topics_get_offset_sends_topic(client_kind, respx_mock):
    """get_offset forwards topic as a query parameter."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/offset").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={"offset": 42})
    )

    # Act
    result = await maybe_await(
        client_kind.subscriber.topics.get_offset(topic="gov.tracss.tracss.v2.cdms")
    )

    # Assert
    url = str(route.calls[0].request.url)
    assert "topic=gov.tracss.tracss.v2.cdms" in url
    assert result == {"offset": 42}


async def test_topics_get_offset_requires_topic(client_kind, respx_mock):
    """get_offset raises TypeError when the required topic kwarg is omitted."""
    # Arrange
    respx_mock.get(f"{BASE}/subscriber/offset").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act / Assert
    with pytest.raises(TypeError):
        await maybe_await(client_kind.subscriber.topics.get_offset())


@parametrize_status_to_error
async def test_topics_get_offset_maps_status_to_exception(
    client_kind, respx_mock, status_code, error_cls
):
    """Each mapped status code on subscriber/offset raises its dedicated exception."""
    # Arrange
    body = {"error": "detail"}
    respx_mock.get(f"{BASE}/subscriber/offset").mock(
        return_value=httpx.Response(status_code, json=body)
    )

    # Act / Assert
    with pytest.raises(error_cls) as exc_info:
        await maybe_await(
            client_kind.subscriber.topics.get_offset(topic="gov.tracss.tracss.v2.cdms")
        )
    assert exc_info.value.status_code == status_code
    assert exc_info.value.body == body


# ── messages.list: required/optional params ─────────────────────────────────


async def test_messages_list_requires_topic(client_kind, respx_mock):
    """messages.list() raises TypeError when the required topic kwarg is omitted."""
    # Arrange
    respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act / Assert
    with pytest.raises(TypeError):
        await maybe_await(client_kind.subscriber.messages.list())


async def test_messages_list_offset_omitted_succeeds(client_kind, respx_mock):
    """Offset is genuinely optional: omitting it succeeds and is absent from the URL."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act
    result = await maybe_await(
        client_kind.subscriber.messages.list(topic="gov.tracss.tracss.v2.cdms")
    )

    # Assert
    url = str(route.calls[0].request.url)
    assert "topic=gov.tracss.tracss.v2.cdms" in url
    assert "offset=" not in url
    assert isinstance(result, ListMessagesResponse)


async def test_messages_list_minimal_args_omits_optional_params(client_kind, respx_mock):
    """Only topic and offset appear when other optional params are omitted."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act
    await maybe_await(
        client_kind.subscriber.messages.list(
            topic="gov.tracss.tracss.v2.cdms", offset="0"
        )
    )

    # Assert
    url = str(route.calls[0].request.url)
    assert "topic=gov.tracss.tracss.v2.cdms" in url
    assert "offset=0" in url
    assert "maxResults" not in url
    assert "filterDesignators" not in url
    assert "fields" not in url


@pytest.mark.parametrize(
    ("kwargs", "expected_fragment"),
    [
        ({"max_results": "50"}, "maxResults=50"),
        ({"filter_designators": "12345"}, "filterDesignators=12345"),
        (
            {"fields": "missDistance,collisionProbability"},
            "fields=missDistance%2CcollisionProbability",
        ),
    ],
    ids=["max_results", "filter_designators", "fields"],
)
async def test_messages_list_optional_param_forwarded_individually(
    client_kind, respx_mock, kwargs, expected_fragment
):
    """Each optional param, passed alone, appears in the outgoing query string."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act
    await maybe_await(
        client_kind.subscriber.messages.list(topic="gov.tracss.tracss.v2.cdms", **kwargs)
    )

    # Assert
    url = str(route.calls[0].request.url)
    assert expected_fragment in url


async def test_messages_list_all_optional_params_combined(client_kind, respx_mock):
    """All optional params, passed together, all appear in the outgoing query string."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act
    await maybe_await(
        client_kind.subscriber.messages.list(
            topic="gov.tracss.tracss.v2.cdms",
            offset="100",
            max_results="50",
            filter_designators="12345",
            fields="missDistance,collisionProbability",
        )
    )

    # Assert
    url = str(route.calls[0].request.url)
    assert "topic=gov.tracss.tracss.v2.cdms" in url
    assert "offset=100" in url
    assert "maxResults=50" in url
    assert "filterDesignators=12345" in url
    assert "fields=missDistance%2CcollisionProbability" in url


# ── filter_designators operator mini-language ───────────────────────────────


@pytest.mark.parametrize(
    "raw_value",
    [
        "12345",
        "<>12345",
        "*123",
        "~*123",
        ">=12345",
        ">12345",
        "<=12345",
        "<12345",
        "12345,67890,34567",
        "12345...67890",
    ],
    ids=[
        "equals",
        "not_equals",
        "like",
        "not_like",
        "gte",
        "gt",
        "lte",
        "lt",
        "in",
        "between",
    ],
)
async def test_messages_list_filter_designators_operator_forwarded_verbatim(
    client_kind, respx_mock, raw_value
):
    """Each filterDesignators operator form is forwarded verbatim, percent-encoded."""
    # Arrange
    route = respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.OK, json={})
    )

    # Act
    await maybe_await(
        client_kind.subscriber.messages.list(
            topic="gov.tracss.tracss.v2.cdms", filter_designators=raw_value
        )
    )

    # Assert
    sent_value = route.calls[0].request.url.params["filterDesignators"]
    assert sent_value == raw_value


# ── messages.list: 204 handling (hand-written wrapper) ──────────────────────


async def test_messages_list_returns_empty_response_on_204(client_kind, respx_mock):
    """The 204-handling wrapper returns an all-None ListMessagesResponse, not an error."""
    # Arrange
    respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(HTTPStatus.NO_CONTENT)
    )

    # Act
    result = await maybe_await(
        client_kind.subscriber.messages.list(
            topic="gov.tracss.tracss.v2.cdms", offset="0"
        )
    )

    # Assert
    assert isinstance(result, ListMessagesResponse)
    assert result.cdm_v2 is None
    assert result.ocm_v2 is None
    assert result.conjunction_data_event is None
    assert result.tip_reports is None
    assert result.anomaly_report is None
    assert result.tracsscat is None


@parametrize_status_to_error
async def test_messages_list_maps_non_204_status_to_exception(
    client_kind, respx_mock, status_code, error_cls
):
    """Non-204 mapped status codes still raise via the 204-handling wrapper."""
    # Arrange
    body = {"error": "detail"}
    respx_mock.get(f"{BASE}/subscriber/messages").mock(
        return_value=httpx.Response(status_code, json=body)
    )

    # Act / Assert
    with pytest.raises(error_cls) as exc_info:
        await maybe_await(
            client_kind.subscriber.messages.list(
                topic="gov.tracss.tracss.v2.cdms", offset="0"
            )
        )
    assert exc_info.value.status_code == status_code
    assert exc_info.value.body == body


# ── subscriber property wrapper wiring ───────────────────────────────────────


def test_subscriber_property_returns_wrapper_subclass(api_client):
    """The sync client's subscriber property is the 204-safe wrapper subclass."""
    from tracss.client import _SubscriberWithMessages

    assert isinstance(api_client.subscriber, _SubscriberWithMessages)


async def test_async_subscriber_property_returns_wrapper_subclass(async_api_client):
    """The async client's subscriber property is the 204-safe wrapper subclass."""
    from tracss.client import _AsyncSubscriberWithMessages

    assert isinstance(async_api_client.subscriber, _AsyncSubscriberWithMessages)
