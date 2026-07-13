#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Apply local patches to the fetched TraCSS OpenAPI specs.

The specs at ``fern/openapi/*/openapi.json`` are consumed two ways: Fern generates
the SDK from them, and Prism mocks them for integration tests. A couple of upstream
quirks must be normalized on the committed spec file itself, because Fern's own
overrides in ``fern/sdks/`` only reach generation - not Prism. ``make specs`` runs
this after fetching:

1. **subscriber** - the ``fields`` query param on ``GET /subscriber/messages`` is
   marked ``required`` even though it is meaningless for non-CDM/OCM topics. Make
   it optional.
2. **metadata** - the tracssCat CSV upload body is typed as a bare binary string,
   so Fern emits no file parameter (sends ``data={}``) and Prism rejects the
   upload. Normalize it to ``object{file}`` so the SDK generates
   ``upload_csv(file=...)`` and Prism mocks a proper multipart file field.

Each patch is idempotent: re-running against an already-patched spec is a no-op.
An unrecognized shape raises :class:`SpecPatchError` naming exactly what changed,
so a silent upstream restructuring fails loudly here rather than producing a wrong
SDK or a broken mock.

Usage:
    python scripts/patch_specs.py [--repo-root PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent


class SpecPatchError(Exception):
    """A spec no longer matches the shape a patch expects (or was never found)."""


def _dig(node: Any, *keys: str, where: str) -> Any:
    """Walk ``keys`` into ``node``, raising a clear error naming the first miss."""
    trail: list[str] = []
    for key in keys:
        trail.append(key)
        if not isinstance(node, dict) or key not in node:
            path = " -> ".join(trail)
            raise SpecPatchError(f"{where}: expected key at {path}, but it is missing")
        node = node[key]
    return node


def patch_fields_optional(spec: dict[str, Any]) -> str:
    """Mark the ``fields`` query param on GET /subscriber/messages optional."""
    params = _dig(
        spec,
        "paths",
        "/subscriber/messages",
        "get",
        "parameters",
        where="subscriber",
    )
    matches = [
        p
        for p in params
        if isinstance(p, dict) and p.get("name") == "fields" and p.get("in") == "query"
    ]
    if len(matches) != 1:
        raise SpecPatchError(
            f"subscriber: expected exactly 1 'fields' query param, found {len(matches)}"
        )
    matches[0]["required"] = False
    return "fields param set optional"


def normalize_csv_upload(spec: dict[str, Any]) -> str:
    """Normalize the tracssCat CSV upload body to ``object{file}`` (idempotent)."""
    content = _dig(
        spec,
        "paths",
        "/metadata/tracssCat/update/csv",
        "post",
        "requestBody",
        "content",
        "multipart/form-data",
        where="metadata",
    )
    schema = content.get("schema", {})
    is_binary = schema.get("type") == "string" and schema.get("format") == "binary"
    is_object = schema.get("type") == "object" and set(schema.get("properties", {})) == {
        "file"
    }
    if not (is_binary or is_object):
        raise SpecPatchError(
            f"metadata: unexpected CSV upload schema, patch may be obsolete: {schema}"
        )
    # Preserve the description from whichever form the upstream spec is in.
    description = schema.get("description") or schema.get("properties", {}).get(
        "file", {}
    ).get("description", "")
    content["schema"] = {
        "type": "object",
        "properties": {
            "file": {"type": "string", "format": "binary", "description": description}
        },
        "required": ["file"],
    }
    return "tracssCat CSV upload body normalized to object{file}"


# (relative-path-under-fern/openapi, patch function) applied in order.
_PATCHES: list[tuple[str, Callable[[dict[str, Any]], str]]] = [
    ("subscriber/openapi.json", patch_fields_optional),
    ("metadata/openapi.json", normalize_csv_upload),
]


def apply_patches(repo_root: Path = _DEFAULT_REPO_ROOT) -> None:
    """Load, patch, and rewrite each spec under ``fern/openapi/`` in place."""
    openapi = repo_root / "fern" / "openapi"
    for rel, patch in _PATCHES:
        path = openapi / rel
        try:
            spec = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise SpecPatchError(
                f"{rel}: not valid JSON (did the fetch return an error page?): {exc}"
            ) from exc
        summary = patch(spec)
        path.write_text(json.dumps(spec, indent=2))
        print(f"  - {rel}: {summary}")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for ``make specs``."""
    parser = argparse.ArgumentParser(description="Patch fetched TraCSS OpenAPI specs.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_DEFAULT_REPO_ROOT,
        help="Repository root containing fern/openapi/ (default: inferred).",
    )
    args = parser.parse_args(argv)
    try:
        apply_patches(args.repo_root)
    except SpecPatchError as exc:
        print(f"patch_specs: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
