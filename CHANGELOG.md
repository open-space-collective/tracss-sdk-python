# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] 2026-06-11

### Added

- Python SDK for the TraCSS Bulk Data, Metadata, and Subscriber REST APIs
- Sync (`TraCSS`) and async (`AsyncTraCSS`) clients with automatic Okta
  client-credentials auth and transparent token refresh
- Full method surface: `subscriber.topics`, `subscriber.messages`,
  `bulk_data.cdm/ocm/tip`, `metadata.cdm/ocm/contact_directory/tracss_cat`
- Unit tests (respx mocks), Prism integration tests, smoke tests
- Fern-driven SDK generation from three OpenAPI specs
- Daily spec-refresh workflow that opens PRs when upstream specs change
- Docs at `tracss.docs.buildwithfern.com`
- CI: fern check, generate-check, lint, typecheck, build, integration, smoke
