# Copyright © Loft Orbital Solutions Inc.
import pytest

from tracss import TraCSS


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: requires Prism mock servers")


@pytest.fixture
def api_client() -> TraCSS:
    """Sync client with a pre-seeded token — bypasses Okta for method unit tests."""
    client = TraCSS(client_id="fake", client_secret="fake")
    client._token = "unit-test-token"
    client._token_expires_at = float("inf")
    return client
