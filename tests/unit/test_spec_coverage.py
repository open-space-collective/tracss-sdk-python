# SPDX-License-Identifier: Apache-2.0
"""Verify every OpenAPI endpoint has an explicit override in fern/sdks/, and vice-versa.

Two complementary invariants are enforced:

1. Every endpoint in the spec has an override entry (forward guard).
   When TraCSS *adds* a new path/method, this test fails, forcing an intentional
   naming decision rather than accepting a Fern auto-generated name.

2. Every override entry refers to an endpoint that still exists in the spec
   (reverse guard).  When TraCSS *removes or renames* an endpoint, this test
   fails, preventing a stale override from silently calling a dead URL.  In an
   SSA pipeline an empty StreamResult from a 404 response is indistinguishable
   from "no conjunction data" unless iteration_errored is explicitly checked.
"""

import inspect
import json
import operator
import re
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).parents[2]

_HTTP_METHODS = frozenset(
    {"delete", "get", "head", "options", "patch", "post", "put", "trace"}
)

_PAIRS = [
    (
        _REPO_ROOT / "fern/openapi/bulk_data/openapi.json",
        _REPO_ROOT / "fern/sdks/bulkdata-overrides.yaml",
    ),
    (
        _REPO_ROOT / "fern/openapi/metadata/openapi.json",
        _REPO_ROOT / "fern/sdks/metadata-overrides.yaml",
    ),
    (
        _REPO_ROOT / "fern/openapi/subscriber/openapi.json",
        _REPO_ROOT / "fern/sdks/subscriber-overrides.yaml",
    ),
]


@pytest.mark.parametrize(
    ("spec_path", "override_path"),
    _PAIRS,
    ids=["bulk_data", "metadata", "subscriber"],
)
def test_all_endpoints_have_overrides(spec_path, override_path):
    spec = json.loads(spec_path.read_text())
    overrides = yaml.safe_load(override_path.read_text())

    spec_endpoints = {
        (path, method)
        for path, path_item in spec.get("paths", {}).items()
        for method in path_item
        if method in _HTTP_METHODS
    }
    override_endpoints = {
        (path, method)
        for path, path_item in (overrides.get("paths") or {}).items()
        for method in path_item
        if method in _HTTP_METHODS
    }

    unmapped = spec_endpoints - override_endpoints
    assert not unmapped, (
        f"Endpoints in {spec_path.name} with no override in {override_path.name}:\n"
        + "\n".join(f"  {method.upper()} {path}" for path, method in sorted(unmapped))
    )


@pytest.mark.parametrize(
    ("spec_path", "override_path"),
    _PAIRS,
    ids=["bulk_data", "metadata", "subscriber"],
)
def test_no_stale_overrides(spec_path, override_path):
    """Every override entry must map to an endpoint that still exists in the spec.

    Catches removed or renamed endpoints before a stale SDK method silently
    calls a dead URL - critical for SSA pipelines where an empty stream is
    indistinguishable from a 404 without explicit iteration_errored checks.

    When this test fails: the spec removed or renamed an endpoint.
    Action: update the override YAML (remove the stale entry or rename the path)
    and update EXPECTED_SURFACE in test_codegen_contract.py to reflect the new
    intended SDK surface.
    """
    spec = json.loads(spec_path.read_text())
    overrides = yaml.safe_load(override_path.read_text())

    spec_endpoints = {
        (path, method)
        for path, path_item in spec.get("paths", {}).items()
        for method in path_item
        if method in _HTTP_METHODS
    }
    override_endpoints = {
        (path, method)
        for path, path_item in (overrides.get("paths") or {}).items()
        for method in path_item
        if method in _HTTP_METHODS
    }

    stale = override_endpoints - spec_endpoints
    assert not stale, (
        f"Overrides in {override_path.name} refer to endpoints"
        f" no longer in {spec_path.name}:\n"
        + "\n".join(f"  {method.upper()} {path}" for path, method in sorted(stale))
        + "\n\nIf an endpoint was removed or renamed upstream, update the override"
        " YAML and EXPECTED_SURFACE in test_codegen_contract.py."
    )


# ---------------------------------------------------------------------------
# Required-parameter snapshot
#
# Fern makes every parameter Optional in the generated Python signatures.
# When TraCSS marks a parameter required in the spec, the SDK cannot enforce
# it - callers silently send requests missing the field and receive 400/422
# errors at runtime with no SDK-level warning.
#
# This snapshot pins the current set of required (non-header) query/body
# parameters.  If TraCSS adds or removes a required parameter the test fails,
# forcing a conscious update: either expose the parameter as non-optional in
# the hand-written client wrapper, or accept the Fern-optional behavior and
# update this snapshot.
#
# Spec source: fern/openapi/{bulk_data,metadata,subscriber}/openapi.json
# Last verified: 2026-06-17
# ---------------------------------------------------------------------------

_REQUIRED_PARAMS_SNAPSHOT: dict[str, dict[tuple[str, str], frozenset[str]]] = {
    "bulk_data": {
        ("get", "/bulkdata/schemas/json/download/{filename}"): frozenset({"filename"}),
        ("get", "/bulkdata/schemas/xsd/download/{filename}"): frozenset({"filename"}),
    },
    "metadata": {
        ("put", "/metadata/contactDirectory/operational/update"): frozenset({"noradIds"}),
        ("get", "/metadata/v2/tracssCdmByOperationalBatch"): frozenset({"batchId"}),
        ("get", "/metadata/schemas/json/download/{filename}"): frozenset({"filename"}),
        ("get", "/metadata/schemas/xsd/download/{filename}"): frozenset({"filename"}),
    },
    "subscriber": {
        ("get", "/subscriber/offset"): frozenset({"topic"}),
        ("get", "/subscriber/messages"): frozenset({"topic"}),
    },
}


def _extract_required_params(
    spec: dict,
) -> dict[tuple[str, str], frozenset[str]]:
    """Return {(method, path): frozenset(required non-header param names)} from a spec."""
    result: dict[tuple[str, str], frozenset[str]] = {}
    for path, path_item in spec.get("paths", {}).items():
        for method, op in path_item.items():
            if method not in _HTTP_METHODS:
                continue
            req = frozenset(
                p["name"]
                for p in op.get("parameters", [])
                if p.get("required") and p.get("in") != "header"
            )
            if req:
                result[(method, path)] = req
    return result


def _diff_required_params(
    actual: dict[tuple[str, str], frozenset[str]],
    expected: dict[tuple[str, str], frozenset[str]],
) -> list[str]:
    """Return human-readable diff lines, empty if actual == expected."""
    added = {k: v for k, v in actual.items() if k not in expected}
    removed = {k: v for k, v in expected.items() if k not in actual}
    changed = {
        k: (expected[k], actual[k])
        for k in actual
        if k in expected and actual[k] != expected[k]
    }
    messages: list[str] = []
    if added:
        messages.append("NEW required params (SDK sends as optional; callers get 400):")
        for (method, path), params in sorted(added.items()):
            messages.append(f"  {method.upper()} {path}: {sorted(params)}")
    if removed:
        messages.append("REMOVED required params (snapshot is stale - update it):")
        for (method, path), params in sorted(removed.items()):
            messages.append(f"  {method.upper()} {path}: {sorted(params)}")
    if changed:
        messages.append("CHANGED required parameter sets:")
        for (method, path), (old, new) in sorted(changed.items()):
            messages.append(
                f"  {method.upper()} {path}: was {sorted(old)}, now {sorted(new)}"
            )
    return messages


# ---------------------------------------------------------------------------
# Spec-to-generated-signature drift detection
#
# Every non-header query/path parameter in the committed OpenAPI spec must
# appear as a snake_case keyword argument in the corresponding generated
# Python method signature.
#
# This replaces a hardcoded parameter-name snapshot.  Instead of maintaining
# a ~150-line dict of camelCase names, the test converts spec param names to
# snake_case using Fern's actual conversion rules and checks them directly
# against the generated code. No snapshot to update; the test automatically
# passes after every successful `fern generate` run.
#
# Failure means:
#   - A spec param was renamed (e.g. noradId → noradIds) but fern generate
#     has not been run yet: the Python signature still has the old name.
#   - A spec param was added but fern generate has not been run yet.
#   - fern generate silently dropped a spec param (generator bug).
#
# Action on failure: run 'make generate' to regenerate from the current specs.
# If the test still fails after regeneration, a fern generator bug dropped a
# spec param, so open an issue and add it to the exclusion list below.
#
# Spec source: fern/openapi/{bulk_data,metadata,subscriber}/openapi.json
# ---------------------------------------------------------------------------

_NAMESPACE_TRIPLES = [
    (
        "bulk_data",
        _REPO_ROOT / "fern/openapi/bulk_data/openapi.json",
        _REPO_ROOT / "fern/sdks/bulkdata-overrides.yaml",
    ),
    (
        "metadata",
        _REPO_ROOT / "fern/openapi/metadata/openapi.json",
        _REPO_ROOT / "fern/sdks/metadata-overrides.yaml",
    ),
    (
        "subscriber",
        _REPO_ROOT / "fern/openapi/subscriber/openapi.json",
        _REPO_ROOT / "fern/sdks/subscriber-overrides.yaml",
    ),
]

# Fern-added params present in Python signatures but not in OpenAPI specs.
_FERN_ADDED_PARAMS = frozenset({"request_options", "self"})


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case using Fern's generator rules.

    Two-pass regex that matches fern-python-sdk's conversion behavior:
    - Pass 1 splits all-caps prefixes (e.g. CAStatus -> CA_Status)
    - Pass 2 splits at lowercase->uppercase boundaries
    - Digit->uppercase is NOT split (object1EphemerisName -> object1ephemeris_name)
    """
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def test_spec_params_present_in_generated_signatures(api_client) -> None:  # noqa: C901, PLR0912
    """Every OpenAPI param must appear as a keyword arg in the Python signature.

    Reads the committed spec files and override YAMLs to build a
    (spec_endpoint) → (python_method) mapping, then verifies that every
    non-header parameter in the spec appears as a snake_case keyword in the
    generated method.

    No snapshot to maintain; fails only when specs drift from generated code.
    After a successful `make generate`, this test always passes automatically.

    When this test fails: run 'make generate' to regenerate the SDK.
    """
    failures: list[str] = []

    for namespace, spec_path, override_path in _NAMESPACE_TRIPLES:
        spec = json.loads(spec_path.read_text())
        overrides = yaml.safe_load(override_path.read_text()) or {}

        # Build (method, path) → (sdk_dotted_path, method_name) from overrides
        endpoint_to_sdk: dict[tuple[str, str], tuple[str, str]] = {}
        for path, path_item in (overrides.get("paths") or {}).items():
            for method, op in (path_item or {}).items():
                if method not in _HTTP_METHODS or not isinstance(op, dict):
                    continue
                group = op.get("x-fern-sdk-group-name") or []
                method_name = op.get("x-fern-sdk-method-name") or ""
                if not group or not method_name:
                    continue
                sdk_dotted = f"{namespace}.{'.'.join(group)}"
                endpoint_to_sdk[(method, path)] = (sdk_dotted, method_name)

        for path, path_item in spec.get("paths", {}).items():
            for method, op in path_item.items():
                if method not in _HTTP_METHODS:
                    continue
                spec_params = frozenset(
                    p["name"] for p in op.get("parameters", []) if p.get("in") != "header"
                )
                if not spec_params:
                    continue
                if (method, path) not in endpoint_to_sdk:
                    continue  # caught by test_all_endpoints_have_overrides

                sdk_dotted, method_name = endpoint_to_sdk[(method, path)]
                try:
                    sub_client = operator.attrgetter(sdk_dotted)(api_client)
                    python_method = getattr(sub_client, method_name)
                except AttributeError as exc:
                    failures.append(
                        f"  {method.upper()} {path}: "
                        f"SDK method {sdk_dotted}.{method_name} not found: {exc}"
                    )
                    continue

                sig = inspect.signature(python_method)
                # Wrapper methods (e.g. _JsonCdmClient.list) use **kwargs and pass
                # through to the generated base class. If the bound method has only
                # VAR_KEYWORD params, walk the MRO to find the explicit-param version.
                if all(
                    p.kind == inspect.Parameter.VAR_KEYWORD
                    for p in sig.parameters.values()
                ):
                    for parent_cls in type(sub_client).__mro__[1:]:
                        if method_name in vars(parent_cls):
                            parent_sig = inspect.signature(
                                getattr(parent_cls, method_name)
                            )
                            if not any(
                                p.kind == inspect.Parameter.VAR_KEYWORD
                                for p in parent_sig.parameters.values()
                            ):
                                sig = parent_sig
                                break

                python_params = frozenset(
                    p for p in sig.parameters if p not in _FERN_ADDED_PARAMS
                )

                missing_in_python = [
                    f"{camel!r} → {_camel_to_snake(camel)!r}"
                    for camel in sorted(spec_params)
                    if _camel_to_snake(camel) not in python_params
                ]
                if missing_in_python:
                    failures.append(
                        f"  {method.upper()} {path} → {sdk_dotted}.{method_name}():"
                        f" {missing_in_python}"
                    )

    assert not failures, (
        "Spec parameters missing from generated Python signatures "
        "(run 'make generate' to sync):\n" + "\n".join(failures)
    )


@pytest.mark.parametrize(
    ("spec_name", "spec_path"),
    [
        ("bulk_data", _PAIRS[0][0]),
        ("metadata", _PAIRS[1][0]),
        ("subscriber", _PAIRS[2][0]),
    ],
    ids=["bulk_data", "metadata", "subscriber"],
)
def test_required_parameters_snapshot(spec_name, spec_path):
    """Required non-header parameters must match the committed snapshot.

    Fern generates all parameters as Optional regardless of the spec's
    required flag.  A new required parameter therefore causes silent 400
    errors at runtime instead of a type error or SDK-level validation.

    When this test fails: a parameter's required status changed upstream.
    Action: decide whether to expose it as non-optional in the hand-written
    client wrapper (recommended for SSA pipelines) or accept the gap and
    update _REQUIRED_PARAMS_SNAPSHOT with an explanatory comment.
    """
    spec = json.loads(spec_path.read_text())
    actual = _extract_required_params(spec)
    expected = _REQUIRED_PARAMS_SNAPSHOT[spec_name]
    messages = _diff_required_params(actual, expected)
    assert not messages, (
        f"Required-parameter snapshot mismatch for {spec_name}:\n"
        + "\n".join(messages)
        + "\n\nUpdate _REQUIRED_PARAMS_SNAPSHOT in test_spec_coverage.py."
    )
