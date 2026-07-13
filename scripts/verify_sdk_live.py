#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Live end-to-end verification of every non-upload SDK method against the TraCSS API.

Usage:
    export TRACSS_CLIENT_ID=...
    export TRACSS_CLIENT_SECRET=...
    uv run python verify_sdk_live.py

Outcomes per row:
  PASS: method returned a usable response (data or empty-but-valid)
  EMPTY: 0 records with no error (data availability, not an SDK bug)
  SKIP: prerequisite missing (e.g. no batch_id to test list_by_operational_batch)
  FAIL: unexpected exception
  403: permission denied (credentials lack access; not an SDK bug)
"""

import sys
import traceback

from tracss import TraCSS
from tracss.core.api_error import ApiError

_STREAM_SAMPLE = 2  # max records to pull from each stream endpoint


def _result(label: str, status: str, detail: str = "") -> dict:
    return {"label": label, "status": status, "detail": detail}


def _run(label: str, fn, results: list) -> object:
    """Call fn(), record outcome in results, return the return value (or None on error)."""
    try:
        value = fn()
        results.append(_result(label, "PASS", _describe(value)))
        return value
    except ApiError as exc:
        if exc.status_code == 403:
            results.append(_result(label, "403", "Forbidden, credentials lack access"))
        elif exc.status_code == 401:
            results.append(_result(label, "403", "Unauthorized"))
        else:
            results.append(_result(label, "FAIL", f"ApiError {exc.status_code}: {str(exc.body)[:120]}"))
        return None
    except Exception:
        results.append(_result(label, "FAIL", traceback.format_exc().splitlines()[-1]))
        return None


def _describe(value) -> str:
    if value is None:
        return "None"
    t = type(value).__name__
    if hasattr(value, "record_count"):
        return f"{t}  record_count={value.record_count}"
    if isinstance(value, list):
        return f"list[{len(value)}]"
    if isinstance(value, dict):
        return f"dict  keys={list(value)[:4]}"
    if isinstance(value, str):
        return f"str  len={len(value)}"
    return t


def _stream(label: str, fn, results: list):
    """Pull up to _STREAM_SAMPLE records from a StreamResult, record outcome."""
    try:
        stream = fn()
        records = []
        for item in stream:
            records.append(item)
            if len(records) >= _STREAM_SAMPLE:
                break
        if records:
            results.append(_result(label, "PASS", f"{len(records)} records, type={type(records[0]).__name__}"))
        else:
            results.append(_result(label, "EMPTY", "stream returned 0 records"))
        return records
    except ApiError as exc:
        if exc.status_code in (403, 401):
            results.append(_result(label, "403", "Forbidden"))
        else:
            results.append(_result(label, "FAIL", f"ApiError {exc.status_code}: {str(exc.body)[:120]}"))
        return []
    except Exception:
        results.append(_result(label, "FAIL", traceback.format_exc().splitlines()[-1]))
        return []


def main() -> None:
    client = TraCSS()
    results: list[dict] = []

    # ── Bulk Data ─────────────────────────────────────────────────────────────

    _stream("bulk_data.cdm.stream",      lambda: client.bulk_data.cdm.stream(size=_STREAM_SAMPLE),      results)
    _stream("bulk_data.ocm.stream",      lambda: client.bulk_data.ocm.stream(size=_STREAM_SAMPLE),      results)
    _stream("bulk_data.tip.stream",      lambda: client.bulk_data.tip.stream(size=_STREAM_SAMPLE),      results)
    _run(   "bulk_data.announcements.list", lambda: client.bulk_data.announcements.list(), results)

    # ── Metadata CDM ──────────────────────────────────────────────────────────

    cdm_list = _run("metadata.cdm.list",     lambda: client.metadata.cdm.list(),     results)

    # list_by_operational_batch requires a batch_id, so try to derive one from cdm.list
    batch_id = None
    if cdm_list is not None and hasattr(cdm_list, "data") and cdm_list.data:
        first = cdm_list.data[0]
        batch_id = getattr(first, "operational_batch_id", None) or getattr(first, "batch_id", None)

    if batch_id:
        _run("metadata.cdm.list_by_operational_batch",
             lambda: client.metadata.cdm.list_by_operational_batch(batch_id=batch_id), results)
    else:
        results.append(_result("metadata.cdm.list_by_operational_batch",    "SKIP", "no batch_id available from cdm.list"))

    # ── Metadata OCM ──────────────────────────────────────────────────────────

    _run("metadata.ocm.list",                          lambda: client.metadata.ocm.list(),     results)
    _run("metadata.ocm.list_by_operational_batch",     lambda: client.metadata.ocm.list_by_operational_batch(),     results)

    # ── Other Metadata ────────────────────────────────────────────────────────

    _run("metadata.contact_directory.list_operational", lambda: client.metadata.contact_directory.list_operational(), results)
    _run("metadata.tracss_cat.list",                    lambda: client.metadata.tracss_cat.list(),           results)
    _run("metadata.tip_reports.list",                   lambda: client.metadata.tip_reports.list(),          results)
    _run("metadata.space_track.list",                   lambda: client.metadata.space_track.list(),          results)
    _run("metadata.space_track.list_nested",            lambda: client.metadata.space_track.list_nested(),   results)
    _run("metadata.schemas.get_xsd",                    lambda: client.metadata.schemas.get_xsd(),           results)
    _run("metadata.schemas.get_json",                   lambda: client.metadata.schemas.get_json(),          results)
    _run("metadata.conjunction_events.list",            lambda: client.metadata.conjunction_events.list(),   results)
    _run("metadata.announcements.list",                 lambda: client.metadata.announcements.list(),        results)

    # ── Subscriber (chained: list → get_offset → messages.list) ──────────────

    topics = _run("subscriber.topics.list", lambda: client.subscriber.topics.list(), results)

    first_topic = None
    if topics is not None:
        if isinstance(topics, list) and topics:
            first_topic = topics[0] if isinstance(topics[0], str) else getattr(topics[0], "name", None)
        elif isinstance(topics, str) and topics.strip():
            first_topic = topics.strip().splitlines()[0]

    if first_topic:
        offset = _run("subscriber.topics.get_offset",
                      lambda: client.subscriber.topics.get_offset(topic=first_topic), results)
        effective_offset = offset if isinstance(offset, int) else 0
        _run("subscriber.messages.list",
             lambda: client.subscriber.messages.list(topic=first_topic, offset=effective_offset), results)
    else:
        results.append(_result("subscriber.topics.get_offset", "SKIP", "no topic from topics.list"))
        results.append(_result("subscriber.messages.list",      "SKIP", "no topic from topics.list"))

    # ── Print results table ───────────────────────────────────────────────────

    col = max(len(r["label"]) for r in results)
    status_icons = {"PASS": "✓", "EMPTY": "○", "SKIP": "–", "403": "🔒", "FAIL": "✗"}
    counts = {"PASS": 0, "EMPTY": 0, "SKIP": 0, "403": 0, "FAIL": 0}

    print()
    print(f"{'Method':<{col}}  Status  Detail")
    print("-" * (col + 50))
    for r in results:
        icon = status_icons.get(r["status"], "?")
        print(f"{r['label']:<{col}}  {icon} {r['status']:<5}  {r['detail']}")
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("-" * (col + 50))
    print(f"PASS={counts['PASS']}  EMPTY={counts['EMPTY']}  SKIP={counts['SKIP']}  403={counts['403']}  FAIL={counts['FAIL']}")

    if counts["FAIL"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
