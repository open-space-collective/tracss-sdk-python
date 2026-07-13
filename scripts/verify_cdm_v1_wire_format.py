#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify a bulk-data stream wire format against the live TraCSS API.

Usage:
    export TRACSS_CLIENT_ID=...
    export TRACSS_CLIENT_SECRET=...
    uv run python verify_cdm_v1_wire_format.py [--path /bulkdata/ocm/v1/stream] [--max-lines 3]

Prints the first N raw lines and classifies the response shape (pretty-printed
JSON vs NDJSON envelope) so you know which parser strategy applies.

Default path: /bulkdata/cdm/v1/stream
"""

import argparse
import base64
import json
import os
import sys

import httpx

OKTA_TOKEN_URL = (
    "https://tracssamu.okta-gov.com/oauth2/aus1358llxDldKxE80j7/v1/token"
)
API_BASE = "https://api.tracss.gov"


def _get_token(client_id: str, client_secret: str) -> str:
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = httpx.post(
        OKTA_TOKEN_URL,
        headers={"Authorization": f"Basic {creds}"},
        data={"grant_type": "client_credentials", "scope": "tracssusername"},
        timeout=15,
    )
    resp.raise_for_status()
    body = resp.json()
    if "access_token" not in body:
        raise ValueError(f"No access_token in response. Keys: {list(body)}")
    return body["access_token"]


def _classify(line_obj: dict) -> str:
    if "headersOnly" in line_obj or "default" in line_obj:
        return "envelope {headersOnly, default}, same as CDM v2 / OCM v1"
    return f"flat object with keys: {list(line_obj)[:6]}..."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default="/bulkdata/cdm/v1/stream",
                        help="API path to stream (default: /bulkdata/cdm/v1/stream)")
    parser.add_argument("--max-lines", type=int, default=3)
    args = parser.parse_args()

    client_id = os.environ.get("TRACSS_CLIENT_ID")
    client_secret = os.environ.get("TRACSS_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit("Set TRACSS_CLIENT_ID and TRACSS_CLIENT_SECRET before running.")

    print("Fetching Okta token...", flush=True)
    token = _get_token(client_id, client_secret)
    print("Token obtained.\n")

    url = f"{API_BASE}{args.path}"
    print(f"GET {url}  (streaming, max {args.max_lines} lines)\n")

    with httpx.stream(
        "GET",
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    ) as resp:
        resp.raise_for_status()
        print(f"HTTP {resp.status_code}  Content-Type: {resp.headers.get('content-type')}\n")

        seen = 0
        for raw_line in resp.iter_lines():
            if not raw_line.strip():
                continue
            print(f"--- line {seen + 1} (raw) ---")
            print(raw_line)
            try:
                obj = json.loads(raw_line)
                print(f"    parsed type : {type(obj).__name__}")
                if isinstance(obj, dict):
                    print(f"    classification: {_classify(obj)}")
                    print(f"    keys ({len(obj)}): {list(obj)[:10]}")
                else:
                    print(f"    value: {str(obj)[:120]}")
            except json.JSONDecodeError as exc:
                print(f"    NOT JSON: {exc}")
            print()
            seen += 1
            if seen >= args.max_lines:
                print(f"(stopped after {args.max_lines} lines; use --max-lines N for more)")
                break

        if seen == 0:
            print("Stream returned 0 records.")
            print("The endpoint may require tighter filters or elevated permissions.")
            print("Try adding ?size=1 or a specific messageId to the URL manually.")


if __name__ == "__main__":
    main()
    