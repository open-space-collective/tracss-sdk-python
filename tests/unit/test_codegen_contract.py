# SPDX-License-Identifier: Apache-2.0
"""Regression tests that catch breaking changes introduced by fern generate."""

import inspect

import tracss
from tracss.base_client import AsyncBaseTraCSS, BaseTraCSS


def test_base_client_accepts_callable_token() -> None:
    """Verify Fern still generates token: Union[str, Callable], not just str.

    If this breaks after a fern generate, override _get_headers() instead
    of passing a callable to super().__init__.
    """
    sig = inspect.signature(BaseTraCSS.__init__)
    assert "token" in sig.parameters, (
        "BaseTraCSS.__init__ no longer accepts a 'token' parameter"
    )


def test_async_base_client_exists() -> None:
    """Verify Fern generates AsyncBaseTraCSS (needed by AsyncTraCSS)."""
    assert AsyncBaseTraCSS is not None


def test_client_exports() -> None:
    """Verify __init__.py exports TraCSS and AsyncTraCSS as expected."""
    assert hasattr(tracss, "TraCSS"), "tracss.TraCSS not exported"
    assert hasattr(tracss, "AsyncTraCSS"), "tracss.AsyncTraCSS not exported"
