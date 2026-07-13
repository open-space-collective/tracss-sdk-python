# SPDX-License-Identifier: Apache-2.0
"""Upload an OCM file to TraCSS.

Usage:
    uv run scripts/upload_ocm.py path/to/file.ocm
    uv run scripts/upload_ocm.py path/to/file.ocm --trigger-ca
    uv run scripts/upload_ocm.py path/to/file.ocm --update-database

Credentials are read from the environment:
    TRACSS_CLIENT_ID, TRACSS_CLIENT_SECRET

Note: The TraCSS metadata OCM endpoint accepts CCSDS OCM files (Object Catalog
Message), not OEM files (Orbit Ephemeris Message). Those are different standards.
"""

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from tracss import TraCSS
from tracss.core.api_error import ApiError

_REPO_ROOT = Path(__file__).parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload an OCM file to TraCSS.")
    parser.add_argument("file", type=Path, help="Path to the OCM file to upload.")
    parser.add_argument(
        "--trigger-ca",
        action="store_true",
        help="Trigger conjunction analysis after upload (operational OCMs only).",
    )
    parser.add_argument(
        "--update-database",
        action="store_true",
        help="Apply OCM data fields to the TraCSS database record.",
    )
    args = parser.parse_args()

    load_dotenv(_REPO_ROOT / ".env")

    path: Path = args.file
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    client = TraCSS()  # reads TRACSS_CLIENT_ID / TRACSS_CLIENT_SECRET from env

    suffix = path.suffix.lower()
    mime = "application/zip" if suffix == ".zip" else "text/plain"

    print(f"Uploading {path.name} ({path.stat().st_size} bytes) ...")
    if args.trigger_ca:
        print("  trigger_ca=True (operational OCMs only)")
    if args.update_database:
        print("  update_database=true")

    with path.open("rb") as fh:
        file_arg = (path.name, fh, mime)
        upload_kwargs = {
            "file": file_arg,
            "trigger_ca": True if args.trigger_ca else None,
            "update_database": "true" if args.update_database else None,
        }
        try:
            result = client.metadata.ocm.upload(**upload_kwargs)
        except ApiError as exc:
            if exc.status_code == 403:
                print(f"error: upload forbidden (403): {exc.body}", file=sys.stderr)
                print(
                    "  This is an account/credential permission issue, not a file "
                    "problem.",
                    file=sys.stderr,
                )
            else:
                print(
                    f"error: upload failed ({exc.status_code}): {exc.body}",
                    file=sys.stderr,
                )
            return 1

    if isinstance(result, str):
        # text/plain 201, e.g. "Uploaded OCM(s) Successfully"
        print(f"Success: {result}")
    else:
        print("Success:")
        print(json.dumps(result, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
