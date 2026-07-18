# Contributing to netbox-atw

Thanks for helping build the best NetBox plugin for the community. This guide covers local dev setup, tests, and the conventions we follow.

## Local dev environment

We ship a `docker-compose.dev.yml` that runs NetBox 4.6 with the plugin mounted as an editable install.

```bash
git clone https://github.com/openjarv/netbox-atw.git
cd netbox-atw
docker compose -f docker-compose.dev.yml up -d
```

NetBox is at http://localhost:8000. The plugin is loaded from the repo via a bind mount; changes to Python files are picked up on container restart.

Login: `admin / admin` (default NetBox dev credentials).

## Running tests

### Pure-Python tests (no NetBox DB needed)

```bash
pip install -e ".[dev]"
pytest netbox_atw/tests/test_importer.py netbox_atw/tests/test_import_specs.py netbox_atw/tests/test_importer_run.py
```

These run anywhere with Python 3.10+ and Django available (no PostgreSQL/Redis required). They are the fast lane for iterating on the import engine, including DB-backed create/update/skip/error paths against an in-memory SQLite fake model.

### Full NetBox test suite (integration)

```bash
docker compose -f docker-compose.dev.yml exec netbox pytest netbox_atw/tests
```

Runs the full suite (model, view, API, device-import integration) inside the NetBox container where the NetBox models are importable.

## Lint and format

```bash
black netbox_atw
isort netbox_atw
flake8 netbox_atw
```

Line length is 120. We target `black` + `isort` (black profile).

## Compatibility matrix

| netbox-atw | NetBox | Python |
|-----------|--------|--------|
| 0.1.x     | 4.6.x  | 3.10, 3.11, 3.12 |

We do not cut the compatibility matrix without CEO sign-off. When a new NetBox minor is released, add it here and to CI **after** the test matrix passes.

## Adding a new import spec

1. Define an `ImportSpec` in `netbox_atw/import_specs.py` with `Column` entries mapping headers to model fields (use `fk_lookup_field` + `fk_model` for FK-by-name).
2. Register it in the `SPECS` dict.
3. Add tests in `netbox_atw/tests/test_import_specs.py` (pure-Python) and, for the first integration of a new model, an integration test like `test_device_import.py`.

## Release process

1. Update `CHANGELOG.md` and `netbox_atw/version.py`.
2. Run the full test suite green across the compatibility matrix.
3. Get CEO sign-off on the first release (and any matrix change).
4. Tag and publish to PyPI (sign-off gated).

## Branching

- Do not commit directly to `main`. Use branches and PRs.
- Branch naming: `<topic>-<short-description>` (e.g. `scaffold-plugin`, `device-import`).
- Squash-merge PRs with a clear commit message + `Co-Authored-By: Paperclip <noreply@paperclip.ing>`.