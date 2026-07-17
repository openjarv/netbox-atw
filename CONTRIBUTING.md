# Contributing to netbox-atw

Thanks for your interest in contributing to **netbox-atw** — the Atw NetBox
plugin for bulk import and population tooling. This guide covers the
expectations, setup, and workflow for contributors.

## Code of Conduct

Participation in this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold it.

## Before you contribute

- **Search existing issues** before opening a new one. Add details to an
  existing issue rather than duplicating it.
- **Open an issue first** for new features or larger changes so we can align
  on approach before you spend time on code. Atw prioritizes features that
  measurably reduce population friction — describe the real-world scenario.
- **One concern per PR** — keep PRs small and focused so review is fast and
  history stays readable.

## Development setup

### Prerequisites

- Python 3.10, 3.11, or 3.12 (see the compatibility matrix in the README)
- A working NetBox development environment (NetBox, PostgreSQL, Redis) — see
  the [NetBox development docs](https://netboxlabs.com/docs/netbox/en/stable/development/)
- `git`

### Get the code

```bash
git clone https://github.com/openjarv/netbox-atw.git
cd netbox-atw
```

### Install dev dependencies

The plugin declares dev extras in `pyproject.toml`:

```bash
pip install -e ".[dev]"
```

This installs `black`, `isort`, `flake8`, `pytest`, and `pytest-django`.

### Run a local NetBox with the plugin

Add `netbox_atw` to your local NetBox dev `PLUGINS` and run
`python manage.py migrate netbox_atw` (or `makemigrations` first if you've
changed the models). The plugin's `min_version` is `3.5.0`.

### Lint and format

```bash
black --check .
isort --check-only .
flake8 .
```

### Run tests

```bash
pytest
```

Two layers of tests:

- **Unit tests** (`netbox_atw/tests/test_importer.py`,
  `test_import_specs.py`) — pure-Python, no NetBox DB required.
- **DB-backed functional tests** (`tests/test_importer_run.py`) — in-memory
  SQLite + a tiny fake app, covering the full create/update/skip/error path,
  dry-run rollback, and per-row error isolation.
- **Integration tests** (`tests/test_importer_integration.py`) — run against
  a NetBox dev instance and exercise the Device importer and the UI wizard.

## Code standards

- Follow the existing style. We use `black` and `isort`, line length 120
  (matching the NetBox ecosystem convention).
- Keep functions and modules small and single-purpose.
- No commented-out code in merged PRs.
- Write tests for new behavior; do not regress existing tests.
- Keep the `CHANGELOG.md` `Unreleased` section updated with your change under
  the right heading (`Added`, `Changed`, `Fixed`, `Removed`).

## Git workflow

1. **Branch from `main`**, do not commit directly to `main`.
2. Use a clear branch prefix and descriptive name, e.g.
   `feat/import-ipam`, `fix/fk-cache`, `docs/usage-guide`.
3. Commit messages: imperative mood, lead with the point — e.g.
   `Add IPAM prefix importer` or `Fix FK cache key for case-sensitive names`.
4. Push your branch and open a PR against `main`.
5. Request review. Address feedback with new commits (avoid force-pushing
   during review unless asked).

## Pull request expectations

- **Title:** concise, describes the change.
- **Description:** what + why. Link the issue (e.g. `Closes #12`). Call out
  anything a reviewer should look at closely.
- **Tests:** new behavior ships with tests; CI must be green.
- **Docs:** if your change affects user-facing behavior, update the README,
  CHANGELOG, and the relevant `docs/` guide in the same PR.
- **New importer?** Follow [docs/adding-an-importer.md](docs/adding-an-importer.md)
  and its pre-merge checklist.
- **Compatibility:** if your change touches the NetBox compatibility surface,
  call it out explicitly and tag a maintainer. Compatibility-matrix changes
  require CEO sign-off.

## Reporting bugs

- Use the **Bug report** issue template.
- Include: NetBox version, plugin version, Python version, OS, exact steps
  to reproduce, expected vs. actual behavior, and relevant logs.
- Reproduce on a clean local NetBox dev instance if you can. Attach the
  ImportJob id if one was created — it captures the raw input and per-row
  result.

## Suggesting features

- Open an issue with the **Feature request** template and describe the
  real-world scenario and the friction it removes. Atw prioritizes features
  that measurably reduce population friction.

## Releasing

Releases are cut by maintainers. The first PyPI release requires CEO
sign-off (see the hiring plan). Versioning follows Semantic Versioning. See
[docs/RELEASING.md](docs/RELEASING.md) for the release runbook.