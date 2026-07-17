# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- User + contributor docs surface: README, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT,
  SECURITY, issue/PR templates, and the `docs/` usage guides (ATW-6).

## [0.1.0] — Unreleased

### Added

- First friction-reducing feature: bulk import / population wizard (ATW-4).
  - Paste CSV/TSV data with human-readable FK references (names, not IDs).
  - Dry-run preview shows create/update/skip/error per row before committing.
  - Create-vs-update decided by a natural key (`name + site` for devices).
  - Per-row validation and error reporting; valid rows commit even when other
    rows error (per-row try/except inside an atomic block).
- **ImportJob** audit model: every run (dry-run or real) is recorded with
  per-row detail, summary counts, raw input, and timestamp — viewable in the
  NetBox UI and REST API (`/api/plugins/atw/import-jobs/`).
- First concrete importer: **Device** (`dcim.Device`) with site, manufacturer,
  device_type, device_role, tenant, platform, serial, asset_tag, status,
  comments columns.
- Model-agnostic importer framework (`netbox_atw.importer`) and an
  `ImportSpec` registry (`netbox_atw.import_specs`) so new scenarios are a
  small spec, not a new view.
- Plugin scaffold: `PluginConfig` (NetBox >= 3.5.0), pyproject, navigation,
  URL routes, templates, REST API, search index, and initial migration (ATW-3).
- Unit tests for the importer framework (no NetBox DB required) and
  DB-backed functional tests (in-memory SQLite + a tiny fake app) covering the
  full create/update/skip/error path, dry-run rollback, and per-row error
  isolation. Integration tests against a NetBox dev instance cover the Device
  importer and the UI wizard.

### Notes

- The `0001_initial` migration is hand-written for the plugin-defined fields.
  Run `python manage.py makemigrations netbox_atw` after install to reconcile
  any `NetBoxModel` base-field drift against the target NetBox version.
- First PyPI release pending CEO sign-off (see `docs/RELEASING.md`).

### Fixed

- _(none yet)_

### Removed

- _(none yet)_

## Release process

Releases are cut by maintainers. Versioning follows Semantic Versioning. The
first PyPI release requires CEO sign-off (role boundary). See
[docs/RELEASING.md](docs/RELEASING.md) for the runbook.