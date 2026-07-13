# SPDX-License-Identifier: Apache-2.0
"""Unit tests for scripts/patch_specs.py (the local OpenAPI spec patches).

These guard the invariants that broke `make specs` before the logic was extracted
from the Makefile: the metadata CSV patch must be idempotent (re-running against an
already-patched spec is a no-op, not a crash), and an unrecognized upstream shape
must fail loudly with a message naming exactly what changed.
"""

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parents[2]

# Canonical result of the CSV normalization, reused across assertions.
_OBJECT_SCHEMA = {
    "type": "object",
    "properties": {
        "file": {"type": "string", "format": "binary", "description": "CSV file"}
    },
    "required": ["file"],
}


@pytest.fixture(scope="module")
def patch_specs():
    """Load scripts/patch_specs.py, which is not an importable package."""
    scripts_dir = str(_REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import patch_specs as module

    return module


def _subscriber_spec(*, required: bool) -> dict:
    return {
        "paths": {
            "/subscriber/messages": {
                "get": {
                    "parameters": [
                        {"name": "topic", "in": "query"},
                        {"name": "fields", "in": "query", "required": required},
                    ]
                }
            }
        }
    }


def _metadata_spec(schema: dict) -> dict:
    return {
        "paths": {
            "/metadata/tracssCat/update/csv": {
                "post": {
                    "requestBody": {
                        "content": {"multipart/form-data": {"schema": schema}}
                    }
                }
            }
        }
    }


def _csv_schema(spec: dict) -> dict:
    path = spec["paths"]["/metadata/tracssCat/update/csv"]
    return path["post"]["requestBody"]["content"]["multipart/form-data"]["schema"]


def _fields_param(spec: dict) -> dict:
    params = spec["paths"]["/subscriber/messages"]["get"]["parameters"]
    return next(p for p in params if p["name"] == "fields")


# --- metadata CSV upload ---------------------------------------------------


def test_normalize_csv_transforms_binary_form(patch_specs):
    spec = _metadata_spec(
        {"type": "string", "format": "binary", "description": "CSV file"}
    )
    patch_specs.normalize_csv_upload(spec)
    assert _csv_schema(spec) == _OBJECT_SCHEMA


def test_normalize_csv_is_idempotent_on_object_form(patch_specs):
    # Starting already in the patched object form (the state that used to crash).
    spec = _metadata_spec(json.loads(json.dumps(_OBJECT_SCHEMA)))
    patch_specs.normalize_csv_upload(spec)
    once = json.dumps(_csv_schema(spec))
    patch_specs.normalize_csv_upload(spec)
    assert json.dumps(_csv_schema(spec)) == once
    assert _csv_schema(spec) == _OBJECT_SCHEMA  # description preserved


def test_normalize_csv_rejects_unexpected_shape(patch_specs):
    spec = _metadata_spec({"type": "array"})
    with pytest.raises(patch_specs.SpecPatchError, match="patch may be obsolete"):
        patch_specs.normalize_csv_upload(spec)


def test_normalize_csv_error_names_missing_path(patch_specs):
    spec = _metadata_spec({"type": "string", "format": "binary"})
    # Remove an intermediate key the patch depends on.
    del spec["paths"]["/metadata/tracssCat/update/csv"]["post"]["requestBody"]
    with pytest.raises(patch_specs.SpecPatchError, match="requestBody"):
        patch_specs.normalize_csv_upload(spec)


# --- subscriber fields -----------------------------------------------------


def test_fields_set_optional(patch_specs):
    spec = _subscriber_spec(required=True)
    patch_specs.patch_fields_optional(spec)
    assert _fields_param(spec)["required"] is False


def test_fields_is_idempotent(patch_specs):
    spec = _subscriber_spec(required=False)
    patch_specs.patch_fields_optional(spec)  # must not raise on already-optional
    assert _fields_param(spec)["required"] is False


def test_fields_requires_exactly_one_match(patch_specs):
    spec = _subscriber_spec(required=True)
    spec["paths"]["/subscriber/messages"]["get"]["parameters"].append(
        {"name": "fields", "in": "query", "required": True}
    )
    with pytest.raises(patch_specs.SpecPatchError, match="exactly 1"):
        patch_specs.patch_fields_optional(spec)


# --- end-to-end file application -------------------------------------------


def test_apply_patches_rewrites_files(patch_specs, tmp_path):
    openapi = tmp_path / "fern" / "openapi"
    (openapi / "subscriber").mkdir(parents=True)
    (openapi / "metadata").mkdir(parents=True)
    (openapi / "subscriber" / "openapi.json").write_text(
        json.dumps(_subscriber_spec(required=True))
    )
    (openapi / "metadata" / "openapi.json").write_text(
        json.dumps(
            _metadata_spec(
                {"type": "string", "format": "binary", "description": "CSV file"}
            )
        )
    )

    patch_specs.apply_patches(tmp_path)

    sub = json.loads((openapi / "subscriber" / "openapi.json").read_text())
    meta = json.loads((openapi / "metadata" / "openapi.json").read_text())
    assert _fields_param(sub)["required"] is False
    assert _csv_schema(meta) == _OBJECT_SCHEMA
