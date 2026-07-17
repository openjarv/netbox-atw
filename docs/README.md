# docs/

Usage guides and examples for **netbox-atw**.

This directory is populated as features land. Each usage guide targets one
real-world scenario and shows the full path: ingest → map → validate →
create/update, with copy-pasteable examples.

## Planned guides

- [ ] `bulk-import.md` — the first bulk import scenario (depends on ATW-4)
- [ ] `examples/` — worked example datasets and mappings (depends on ATW-4)
- [ ] `RELEASING.md` — release runbook (depends on ATW-3 / ATW-5)
- [ ] `compatibility-matrix.md` — NetBox × Python matrix (depends on ATW-3 / ATW-5)

## Guide template

When you add a guide, follow this shape so docs stay consistent and a new user
can complete the task from the guide alone:

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