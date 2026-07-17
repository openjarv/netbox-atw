# docs/

User + contributor documentation for **netbox-atw** — the Atw NetBox plugin
for bulk import and population tooling.

## Usage guides

- [bulk-import.md](bulk-import.md) — full bulk-import walkthrough (the first
  shipped scenario: Device population).
- [examples/worked-examples.md](examples/worked-examples.md) — copy-pasteable
  datasets for the import wizard.
- [examples/devices.csv](examples/devices.csv) — minimal starter dataset.
- [api.md](api.md) — REST API reference for the `ImportJob` audit model.
- [adding-an-importer.md](adding-an-importer.md) — how to add a new target
  to the model-agnostic importer framework.
- [RELEASING.md](RELEASING.md) — release runbook (first PyPI release
  requires CEO sign-off).

## Top-level docs

- [../README.md](../README.md) — install, features, quick usage
- [../CHANGELOG.md](../CHANGELOG.md) — release history
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — how to contribute
- [../CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) — community standards
- [../SECURITY.md](../SECURITY.md) — reporting vulnerabilities

## Guide template

When you add a scenario guide, follow this shape so a new user can complete
the task from the guide alone:

```
# <Scenario name>

## Goal
One sentence: what real-world friction this removes.

## Prerequisites
- Plugin installed (see README)
- NetBox version, required data already in NetBox

## Inputs
The source data shape (file, API response, etc.).

## Steps
1. ...
2. ...

## Validation
How the user confirms it worked.

## Troubleshooting
Common failures and fixes.
```