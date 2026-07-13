# SPDX-License-Identifier: Apache-2.0
"""Regression tests that catch breaking changes introduced by fern generate."""

import inspect
import operator
from pathlib import Path

import tracss
from tracss.base_client import AsyncBaseTraCSS, BaseTraCSS
from tracss.bulk_data.cdm.types import StreamCdmResponse
from tracss.bulk_data.ocm.types import StreamOcmResponse
from tracss.metadata.cdm.types import ListCdmResponse
from tracss.metadata.ocm.types import ListOcmResponse
from tracss.subscriber.messages.types import ListMessagesResponse
from tracss.subscriber.types import TracssCdmV2

# Hard-coded snapshot of every public API method on each generated sub-client.
# Update this dict when intentionally adding, removing, or renaming a method -
# an unexpected diff here means a spec or generator change needs an explicit override.
EXPECTED_SURFACE = {
    "bulk_data.cdm": {"stream"},
    "bulk_data.ocm": {"stream"},
    "bulk_data.tip": {"stream"},
    "bulk_data.announcements": {"list"},
    "bulk_data.schemas": {"get_json", "download_json", "get_xsd", "download_xsd"},
    "metadata.contact_directory": {"list_operational", "update_operational"},
    "metadata.ocm": {"list", "list_by_operational_batch", "upload"},
    "metadata.cdm": {"list", "list_by_operational_batch"},
    "metadata.tracss_cat": {"list", "upload_csv"},
    "metadata.tip_reports": {"list"},
    "metadata.space_track": {"list", "list_nested"},
    "metadata.schemas": {"get_xsd", "download_xsd", "get_json", "download_json"},
    "metadata.conjunction_events": {"list"},
    "metadata.announcements": {"list"},
    "metadata.translation_errors": {"list"},
    "subscriber.topics": {"list", "get_offset"},
    "subscriber.messages": {"list"},
}


def test_base_client_accepts_callable_token() -> None:
    """Verify Fern still generates token: Union[str, Callable], not just str.

    If this breaks after a fern generate, override _get_headers() instead
    of passing a callable to super().__init__.
    """
    sig = inspect.signature(BaseTraCSS.__init__)
    assert "token" in sig.parameters, (
        "BaseTraCSS.__init__ no longer accepts a 'token' parameter"
    )
    annotation = sig.parameters["token"].annotation
    ann_str = str(annotation)
    assert "Callable" in ann_str or "callable" in ann_str.lower(), (
        f"token param no longer accepts a Callable (annotation: {ann_str!r}). "
        "If Fern narrowed this to str-only, switch AsyncTraCSS to override "
        "_client_wrapper.get_headers() instead of passing token=callable."
    )


def test_async_base_client_accepts_callable_async_token() -> None:
    """AsyncBaseTraCSS must accept async_token: Callable, not just a coroutine literal.

    The sync path is guarded by test_base_client_accepts_callable_token; this
    mirrors that check for the async path. If Fern narrows async_token to a
    bare coroutine type, AsyncTraCSS._aget_token would need to be passed
    differently, likely by overriding _client_wrapper.get_headers() instead.
    """
    sig = inspect.signature(AsyncBaseTraCSS.__init__)
    param_name = next((p for p in ("async_token", "token") if p in sig.parameters), None)
    assert param_name is not None, (
        "AsyncBaseTraCSS.__init__ has neither 'async_token' nor 'token' parameter"
    )
    annotation = sig.parameters[param_name].annotation
    ann_str = str(annotation)
    assert "Callable" in ann_str or "callable" in ann_str.lower(), (
        f"async_token param no longer accepts a Callable (annotation: {ann_str!r}). "
        "If Fern narrowed this, switch AsyncTraCSS to override "
        "_client_wrapper.get_headers() instead."
    )


def test_async_base_client_exists() -> None:
    """Verify Fern generates AsyncBaseTraCSS (needed by AsyncTraCSS)."""
    assert AsyncBaseTraCSS is not None


def test_client_exports() -> None:
    """Verify __init__.py exports TraCSS and AsyncTraCSS as expected."""
    assert hasattr(tracss, "TraCSS"), "tracss.TraCSS not exported"
    assert hasattr(tracss, "AsyncTraCSS"), "tracss.AsyncTraCSS not exported"


def test_public_types_importable() -> None:
    """Key user-facing types must remain importable from their generated paths.

    Fails if a generator upgrade reorganizes modules or renames a type in a way
    that breaks callers. Not a full snapshot - generator-check diff covers the rest.
    """
    assert all(
        t is not None
        for t in [
            StreamCdmResponse,
            StreamOcmResponse,
            ListCdmResponse,
            ListOcmResponse,
            ListMessagesResponse,
            TracssCdmV2,
        ]
    )


def test_method_surface_matches_snapshot(api_client) -> None:
    """Generated SDK surface must exactly match EXPECTED_SURFACE.

    Fails on addition (e.g. auto-named v3 method), removal, or rename.
    with_raw_response / with_streaming_response are @property, not methods,
    so inspect.ismethod excludes them without an explicit filter.
    """
    for dotted_path, expected in EXPECTED_SURFACE.items():
        sub_client = operator.attrgetter(dotted_path)(api_client)
        actual = {
            name
            for name, _ in inspect.getmembers(sub_client, predicate=inspect.ismethod)
            if not name.startswith("_")
        }
        assert actual == expected, (
            f"{dotted_path}: method surface mismatch\n"
            f"  unexpected: {actual - expected}\n"
            f"  missing:    {expected - actual}"
        )


def test_json_cdm_wrapper_exposes_all_generated_methods() -> None:
    """_JsonCdmClient must expose every public method of the generated CdmClient.

    If _JsonCdmClient accidentally hides an inherited method after a generator
    update, callers would silently lose access to it.  The snapshot test above
    only catches methods that were already listed in EXPECTED_SURFACE; this test
    catches any drop not in the snapshot.
    """
    from tracss.client import _JsonCdmClient
    from tracss.metadata.cdm.client import CdmClient

    generated = {
        name
        for name, _ in inspect.getmembers(CdmClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    wrapped = {
        name
        for name, _ in inspect.getmembers(_JsonCdmClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    missing = generated - wrapped
    assert not missing, (
        f"_JsonCdmClient is missing these methods from the generated CdmClient: {missing}"
    )


def test_json_ocm_wrapper_exposes_all_generated_methods() -> None:
    """_JsonOcmClient must expose every public method of the generated OcmClient."""
    from tracss.client import _JsonOcmClient
    from tracss.metadata.ocm.client import OcmClient

    generated = {
        name
        for name, _ in inspect.getmembers(OcmClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    wrapped = {
        name
        for name, _ in inspect.getmembers(_JsonOcmClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    missing = generated - wrapped
    assert not missing, (
        f"_JsonOcmClient is missing these methods from the generated OcmClient: {missing}"
    )


def test_json_tip_reports_wrapper_exposes_all_generated_methods() -> None:
    """_JsonTipReportsClient must expose every public method of TipReportsClient."""
    from tracss.client import _JsonTipReportsClient
    from tracss.metadata.tip_reports.client import TipReportsClient

    generated = {
        name
        for name, _ in inspect.getmembers(TipReportsClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    wrapped = {
        name
        for name, _ in inspect.getmembers(
            _JsonTipReportsClient, predicate=inspect.isfunction
        )
        if not name.startswith("_")
    }
    missing = generated - wrapped
    assert not missing, (
        f"_JsonTipReportsClient is missing these methods from TipReportsClient: {missing}"
    )


def test_json_ocm_wrapper_exposes_batch_methods() -> None:
    """_JsonOcmClient must expose list_by_operational_batch (204-fix method)."""
    from tracss.client import _JsonOcmClient

    assert hasattr(_JsonOcmClient, "list_by_operational_batch"), (
        "_JsonOcmClient missing list_by_operational_batch"
    )


def test_post_generate_patches_applied() -> None:
    """Verify all make post-generate patches were applied after the last fern generate.

    The post-generate sed commands exit 0 even when they match nothing, so this
    test is the only signal that a patch silently no-oped (e.g. Fern changed the
    generated file structure so a sed pattern no longer matched).
    """
    repo_root = Path(__file__).parent.parent.parent

    # Patch 1: org-name fix in the generated aiohttp test file
    aiohttp_test = repo_root / "sdks/python/tracss/tests/test_aiohttp_autodetect.py"
    if aiohttp_test.exists():
        content = aiohttp_test.read_text()
        assert "open-space-collective" not in content, (
            "post-generate org-name patch not applied. Run 'make post-generate' "
            "or check that the sed pattern still matches the generated file"
        )

    # Patches 2-4: RawResponse export and __version__ wiring in __init__.py
    init_py = repo_root / "sdks/python/tracss/__init__.py"
    init_content = init_py.read_text()
    assert '"RawResponse"' in init_content, (
        "post-generate RawResponse export patch not applied: "
        "'RawResponse' key missing from _dynamic_imports in __init__.py"
    )
    assert '"__version__"' in init_content, (
        "post-generate __version__ patch not applied: "
        "'__version__' key missing from _dynamic_imports in __init__.py"
    )

    # Patch 5: token=<token> doc fix in the shipped README.md and reference.md.
    # Fern emits TraCSS(token="<token>") examples, which raise TypeError against the
    # public constructor (it forwards **kwargs into BaseTraCSS(token=...)). The
    # post-generate sed rewrites them to client_id=/client_secret=.
    for rel in ("sdks/python/tracss/README.md", "sdks/python/tracss/reference.md"):
        doc = repo_root / rel
        assert 'token="<token>"' not in doc.read_text(), (
            f"post-generate token=<token> doc fix not applied to {rel}. "
            "Run 'make post-generate' or check the sed still matches."
        )

    # Patch 6: the RawResponse __all__ export must not be duplicated. The
    # post-generate sed runs every invocation; without an idempotency guard a
    # re-run appends "RawResponse" to __all__ again.
    assert tracss.__all__.count("RawResponse") == 1, (
        f'"RawResponse" appears {tracss.__all__.count("RawResponse")}x in __all__; '
        "the post-generate __all__ sed is missing its idempotency guard"
    )


def test_generated_group_clients_expose_lazy_subclient_attributes(api_client) -> None:
    """Generated group clients must keep the lazy-init attributes the wrappers drive.

    The client.py wrappers subclass MetadataClient/BulkDataClient/SubscriberClient and
    override their sub-client @property getters, which read and assign ``self._cdm``,
    ``self._ocm``, ``self._messages``, etc. If a generator upgrade switched these group
    clients to the dynamic ``__getattr__`` import scheme the top-level ``__init__.py``
    already uses, those attributes would vanish and the overrides would silently break
    (the method-surface snapshot only checks method names, not attributes). ``vars()``
    is used deliberately so a dynamic ``__getattr__`` cannot mask a missing attribute.
    """
    from tracss.bulk_data.client import BulkDataClient
    from tracss.metadata.client import MetadataClient
    from tracss.subscriber.client import SubscriberClient

    wrapper = api_client._client_wrapper
    expectations = [
        (
            MetadataClient(client_wrapper=wrapper),
            [
                "_cdm",
                "_ocm",
                "_tip_reports",
                "_space_track",
                "_conjunction_events",
                "_tracss_cat",
                "_contact_directory",
            ],
        ),
        (
            BulkDataClient(client_wrapper=wrapper),
            ["_cdm", "_ocm", "_tip", "_announcements"],
        ),
        (SubscriberClient(client_wrapper=wrapper), ["_messages"]),
    ]
    for instance, attrs in expectations:
        instance_vars = vars(instance)
        for attr in attrs:
            assert attr in instance_vars, (
                f"{type(instance).__name__} no longer sets '{attr}' in __init__; the "
                "lazy-init pattern the client.py wrapper property overrides depend on "
                "has changed (e.g. Fern moved to a dynamic __getattr__ scheme)"
            )
            assert instance_vars[attr] is None, (
                f"{type(instance).__name__}.{attr} no longer initializes to None"
            )


def test_wrapped_methods_preserve_generated_signature() -> None:
    """Wrapper methods must expose the generated method's parameters at runtime.

    The _Json*/_Streaming* wrappers take ``**kwargs``; ``@_wrap_generated``
    (functools.wraps + __signature__) restores the real parameter list so
    help()/inspect/IDEs show it. If a wrapper method is added or edited without the
    decorator, its signature silently reverts to ``(**kwargs)`` - this catches that,
    and also flags parameter drift between the wrapper and the generated method.
    """
    from tracss import client as c
    from tracss.bulk_data.cdm.client import AsyncCdmClient as AsyncBulkCdm
    from tracss.bulk_data.cdm.client import CdmClient as BulkCdm
    from tracss.bulk_data.ocm.client import AsyncOcmClient as AsyncBulkOcm
    from tracss.bulk_data.ocm.client import OcmClient as BulkOcm
    from tracss.bulk_data.tip.client import AsyncTipClient as AsyncBulkTip
    from tracss.bulk_data.tip.client import TipClient as BulkTip
    from tracss.metadata.cdm.client import AsyncCdmClient, CdmClient
    from tracss.metadata.conjunction_events.client import (
        AsyncConjunctionEventsClient,
        ConjunctionEventsClient,
    )
    from tracss.metadata.contact_directory.client import (
        AsyncContactDirectoryClient,
        ContactDirectoryClient,
    )
    from tracss.metadata.ocm.client import AsyncOcmClient, OcmClient
    from tracss.metadata.space_track.client import AsyncSpaceTrackClient, SpaceTrackClient
    from tracss.metadata.tip_reports.client import AsyncTipReportsClient, TipReportsClient
    from tracss.metadata.tracss_cat.client import AsyncTracssCatClient, TracssCatClient
    from tracss.subscriber.messages.client import AsyncMessagesClient, MessagesClient

    cases = [
        (c._JsonCdmClient, CdmClient, ["list", "list_by_operational_batch"]),
        (c._AsyncJsonCdmClient, AsyncCdmClient, ["list", "list_by_operational_batch"]),
        (c._JsonOcmClient, OcmClient, ["list", "list_by_operational_batch", "upload"]),
        (
            c._AsyncJsonOcmClient,
            AsyncOcmClient,
            ["list", "list_by_operational_batch", "upload"],
        ),
        (c._JsonTipReportsClient, TipReportsClient, ["list"]),
        (c._AsyncJsonTipReportsClient, AsyncTipReportsClient, ["list"]),
        (c._JsonMessagesClient, MessagesClient, ["list"]),
        (c._AsyncJsonMessagesClient, AsyncMessagesClient, ["list"]),
        (c._EmptySafeSpaceTrackClient, SpaceTrackClient, ["list", "list_nested"]),
        (
            c._AsyncEmptySafeSpaceTrackClient,
            AsyncSpaceTrackClient,
            ["list", "list_nested"],
        ),
        (c._EmptySafeConjunctionEventsClient, ConjunctionEventsClient, ["list"]),
        (
            c._AsyncEmptySafeConjunctionEventsClient,
            AsyncConjunctionEventsClient,
            ["list"],
        ),
        (c._EmptySafeTracssCatClient, TracssCatClient, ["list"]),
        (c._AsyncEmptySafeTracssCatClient, AsyncTracssCatClient, ["list"]),
        (
            c._EmptySafeContactDirectoryClient,
            ContactDirectoryClient,
            ["list_operational"],
        ),
        (
            c._AsyncEmptySafeContactDirectoryClient,
            AsyncContactDirectoryClient,
            ["list_operational"],
        ),
        (c._StreamingCdmBulkClient, BulkCdm, ["stream"]),
        (c._AsyncStreamingCdmBulkClient, AsyncBulkCdm, ["stream"]),
        (c._StreamingOcmBulkClient, BulkOcm, ["stream"]),
        (c._AsyncStreamingOcmBulkClient, AsyncBulkOcm, ["stream"]),
        (c._StreamingTipBulkClient, BulkTip, ["stream"]),
        (c._AsyncStreamingTipBulkClient, AsyncBulkTip, ["stream"]),
    ]

    for wrapper_cls, generated_cls, methods in cases:
        for method in methods:
            wparams = [
                p
                for p in inspect.signature(getattr(wrapper_cls, method)).parameters
                if p != "self"
            ]
            gparams = [
                p
                for p in inspect.signature(getattr(generated_cls, method)).parameters
                if p != "self"
            ]
            assert wparams != ["kwargs"], (
                f"{wrapper_cls.__name__}.{method} still shows (**kwargs); "
                "the @_wrap_generated decorator is missing or ineffective"
            )
            assert wparams == gparams, (
                f"{wrapper_cls.__name__}.{method} signature drifted from "
                f"{generated_cls.__name__}.{method}\n"
                f"  wrapper:   {wparams}\n"
                f"  generated: {gparams}"
            )


def test_format_sensitive_methods_are_explicitly_wrapped() -> None:
    """Verify format-sensitive generated methods are explicitly overridden.

    Any generated CDM/OCM/TIP method with a 'format' param must be directly
    defined on the corresponding wrapper class, not just inherited.

    Inherited methods skip the _call_or_raw() format-defaulting logic, so a new
    format-sensitive endpoint added by Fern would silently return KVN text instead
    of JSON. This test catches that before it reaches callers.
    """
    from tracss.client import _JsonCdmClient, _JsonOcmClient, _JsonTipReportsClient
    from tracss.metadata.cdm.client import CdmClient
    from tracss.metadata.ocm.client import OcmClient
    from tracss.metadata.tip_reports.client import TipReportsClient

    pairs = [
        (CdmClient, _JsonCdmClient),
        (OcmClient, _JsonOcmClient),
        (TipReportsClient, _JsonTipReportsClient),
    ]
    missing = []
    for generated_cls, wrapper_cls in pairs:
        for name, fn in inspect.getmembers(generated_cls, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            sig = inspect.signature(fn)
            if "format" not in sig.parameters:
                continue
            if name not in vars(wrapper_cls):
                missing.append(
                    f"{generated_cls.__name__}.{name} has a 'format' param "
                    f"but {wrapper_cls.__name__} does not override it"
                )

    assert not missing, (
        "Format-sensitive methods not wrapped. Add _call_or_raw() overrides in "
        "client.py for:\n  " + "\n  ".join(missing)
    )
