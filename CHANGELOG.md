# Changelog

All notable changes to netbox-atw are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Initial NetBox plugin scaffold (installable, importable, runs against NetBox 4.6.x).
- `ImportJob` bookkeeping model + REST API + GraphQL type for auditing imports.
- Model-agnostic import engine (`importer.py`) with CSV/TSV parsing, header validation, foreign-key-by-name resolution, and dry-run preview via savepoint rollback.
- First concrete import spec: **Device** population with FK-by-name resolution for site, manufacturer, device type, role, tenant, platform.
- Two-step import wizard UI (paste → dry-run preview → commit).
- Navigation menu entries (Import Jobs, New Import).
- Test suite: pure-Python importer/parser tests, model tests, view tests, API tests, device-import integration test.
- Local dev environment via `docker-compose.dev.yml` (NetBox + PostgreSQL + Redis).
- CI workflow (GitHub Actions) running the test matrix.

### Compatibility

- NetBox 4.6.x (current: 4.6.5)
- Python 3.10, 3.11, 3.12