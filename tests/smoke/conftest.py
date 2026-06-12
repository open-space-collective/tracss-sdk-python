# SPDX-License-Identifier: Apache-2.0
"""Fixtures for smoke tests against the live TraCSS API."""

import pytest

from tracss import TraCSS


@pytest.fixture(scope="session")
def live_client() -> TraCSS:
    """Sync TraCSS client using real credentials from env vars.

    Requires TRACSS_CLIENT_ID and TRACSS_CLIENT_SECRET to be set.
    TRACSS_OKTA_DOMAIN and TRACSS_OKTA_AUTH_SERVER_ID fall back to built-in
    defaults if not set.
    """
    return TraCSS()
