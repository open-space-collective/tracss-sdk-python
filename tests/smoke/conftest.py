# SPDX-License-Identifier: Apache-2.0
"""Fixtures for smoke tests against the live TraCSS API."""

import json
from http import HTTPStatus

import pytest

from tracss import TraCSS
from tracss.core.api_error import ApiError

# Status codes that mean "these credentials lack subscriber access" rather than an
# SDK bug. Per-namespace error classes differ, so guard on the base ApiError +
# status_code (matches scripts/verify_sdk_live.py's treatment of 401/403).
_ACCESS_DENIED_STATUSES = frozenset(
    {HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}
)


@pytest.fixture(scope="session")
def live_client() -> TraCSS:
    """Sync TraCSS client using real credentials from env vars.

    Requires TRACSS_CLIENT_ID and TRACSS_CLIENT_SECRET to be set.
    TRACSS_OKTA_DOMAIN and TRACSS_OKTA_AUTH_SERVER_ID fall back to built-in
    defaults if not set.
    """
    return TraCSS()


@pytest.fixture(scope="session")
def live_topics(live_client: TraCSS) -> list[str]:
    """Return available subscriber topic names from the live API.

    Returns an empty list if no topics are available or the response cannot
    be parsed. Subscriber subtests skip when the list is empty.
    """
    try:
        raw = live_client.subscriber.topics.list()
    except ApiError as exc:
        if exc.status_code in _ACCESS_DENIED_STATUSES:
            return []
        raise
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(t) for t in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    for sep in ("\n", ","):
        parts = [p.strip() for p in raw.split(sep) if p.strip()]
        if parts:
            return parts
    return []
