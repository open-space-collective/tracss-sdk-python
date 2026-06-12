# tracss

Python SDK for the three [TraCSS](https://tracss.gov) REST APIs — Bulk Data, Metadata, and Subscriber.

[![CI](https://github.com/open-space-collective/tracss-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/open-space-collective/tracss-sdk-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tracss)](https://pypi.org/project/tracss/)
[![Docs](https://img.shields.io/badge/docs-buildwithfern-blue)](https://tracss.docs.buildwithfern.com)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Community SDK - not an official TraCSS product.**
> Built and maintained by [Loft Orbital](https://www.loftorbital.com) via the
> [Open Space Collective](https://github.com/open-space-collective) organization,
> using [Fern](https://buildwithfern.com). Not affiliated with, endorsed by, or
> officially supported by the Office of Space Commerce (OSC) or NOAA.

> **0.x alpha** — the API surface is stabilising; breaking changes are possible before 1.0.

## Install

```bash
pip install tracss
```

## Quick start

```python
from tracss import TraCSS

client = TraCSS()  # reads TRACSS_CLIENT_ID and TRACSS_CLIENT_SECRET from env

# List available Kafka topics
topics = client.subscriber.topics.list()

# Stream CDM conjunction messages
data = client.bulk_data.cdm.stream()

# List conjunction data messages from the metadata catalog
cdms = client.metadata.cdm.list()
```

The async client works the same way:

```python
from tracss import AsyncTraCSS

async with AsyncTraCSS() as client:
    topics = await client.subscriber.topics.list()
```

## Auth

TraCSS uses Okta client credentials. You need two things:

```bash
export TRACSS_CLIENT_ID=your-client-id
export TRACSS_CLIENT_SECRET=your-client-secret
```

Tokens are fetched lazily and refreshed automatically — you never touch auth in application code. See the [authentication docs](https://tracss.docs.buildwithfern.com/authentication) for full details, including custom Okta domains.

## What's in the box

| Namespace | Key methods |
|---|---|
| `client.subscriber.topics` | `list()`, `get_offset(topic=…)` |
| `client.subscriber.messages` | `list(topic=…, offset=…)` |
| `client.bulk_data.cdm` | `stream()`, `stream_v1()` |
| `client.bulk_data.ocm` | `stream()`, `stream_v1()` |
| `client.bulk_data.tip` | `stream()` |
| `client.metadata.cdm` | `list()`, `list_v1()`, `list_by_operational_batch()` |
| `client.metadata.ocm` | `upload()`, `upload_v1()`, `list()`, `list_v1()` |
| `client.metadata.contact_directory` | `list_operational()`, `update_operational()` |
| `client.metadata.tracss_cat` | `list()`, `upload_csv()` |

Full reference: [tracss.docs.buildwithfern.com](https://tracss.docs.buildwithfern.com)

## How this repo works

This is a **code-generation monorepo**, not a hand-written SDK:

```
TraCSS OpenAPI specs ──► fern generate ──► sdks/python/  (committed)
   fern/openapi/*/            │                 │
   openapi.json          fern/sdks/overrides  the package
   (make specs fetches here)  │               you install
                              │
                         fern docs dev ──► docs site at
                         fern/docs.yml     tracss.docs.buildwithfern.com
                         fern/docs/pages/  + Python SDK snippet
                                            per endpoint
```

The three OpenAPI specs live under `fern/openapi/*/`. A daily scheduled workflow (`spec-refresh.yml`) fetches them from the live API, regenerates the SDK with [Fern](https://buildwithfern.com), and opens a PR. The only hand-written file in the SDK is `sdks/python/tracss/client.py` — the Okta auth wrapper.

## Docs site

The docs site at [tracss.docs.buildwithfern.com](https://tracss.docs.buildwithfern.com) is built from the same sources as the SDK:

| Source | Contents |
|---|---|
| `fern/docs.yml` | Navigation structure, colors, logo |
| `fern/docs/pages/*.mdx` | Prose pages (Getting Started, Authentication) |
| `fern/openapi/*/openapi.json` | API reference — same specs `make specs` refreshes |
| `fern/sdks/*-overrides.yaml` | Method names applied to both SDK and docs |

Every API endpoint page automatically shows a Python SDK code snippet (e.g. `client.subscriber.topics.list()`) alongside the HTTP reference. These are generated from the `snippets: python: tracss` entry in `docs.yml` and the `x-fern-sdk-*` method-name overrides.

## Dev setup

| Tool | Purpose |
|---|---|
| Python 3.10+ | runtime |
| [uv](https://docs.astral.sh/uv/) | package management |
| Node 20 | Fern CLI runtime |
| [Fern CLI](https://buildwithfern.com) `5.46.0` | SDK generation |
| [Prism](https://stoplight.io/open-source/prism) | integration test mock server |

```bash
uv sync                          # install workspace deps
pre-commit install                # wire git hooks
npm install -g fern-api@5.46.0   # Fern CLI
npm install -g @stoplight/prism-cli  # Prism (for integration tests)
```

## Useful make targets

```bash
# Quality
make lint          # ruff check + format check
make fmt           # auto-fix
make typecheck     # mypy (hand-written code only)
make test          # unit tests

# Integration
make prism-all     # start mock servers (ports 4010-4012)
make integration   # integration tests against Prism

# Fern & specs
make specs         # fetch latest OpenAPI specs (shows diff)
make check         # validate fern config
make generate      # regenerate SDK locally
make build         # build + validate the wheel

# Docs
make docs-dev      # live preview at localhost:3000 — hot-reloads on file changes
make docs-preview  # shareable staging URL (needs FERN_TOKEN or: fern login first)

# Live API
make smoke         # smoke tests (needs real TRACSS_* credentials)
```

`make help` lists everything.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: most of `sdks/python/` is generated — changes there are overwritten on the next `fern generate`. If you want to change SDK behavior, start with `fern/sdks/` (method-name overrides) or open an issue.
