# netbox-atw

The **Atw** [NetBox](https://netbox.dev) plugin — bulk import and population
tooling that reduces the friction of getting real-world data into NetBox.

The first shipped feature is a **bulk import wizard**: paste CSV/TSV data with
human-readable foreign-key references (e.g. `Site=AMS01`, `Manufacturer=Cisco`)
instead of NetBox primary keys, preview the exact create/update/skip outcome
as a dry run, then commit. Every run (dry-run or real) is recorded as an
**ImportJob** so you can audit population history from the NetBox UI or the
REST API. New importers are added via a small, model-agnostic spec — see
[Adding a new importer](#adding-a-new-importer).

> **Status:** 0.1.0 (pre-release). Not yet on PyPI — install from source for
> now. First PyPI release requires CEO sign-off (see [RELEASING](docs/RELEASING.md)).

## Features

- Bulk import wizard: paste → dry-run preview → commit
- Foreign keys resolved by **name**, not NetBox PK
- Create-vs-update decided by a natural key (e.g. `name + site` for devices)
- Per-row validation and error reporting; valid rows commit even when other
  rows error
- **ImportJob** audit model: every run (dry-run or real) is recorded with
  per-row detail, summary counts, and the raw input — viewable in the NetBox
  UI and REST API
- REST API for ImportJob at `/api/plugins/atw/import-jobs/`
- Model-agnostic importer framework (`netbox_atw.importer`) for future
  scenarios
- First scenario: **Device** population

## Compatibility

| NetBox | Python | Status |
|--------|--------|--------|
| >= 3.5 | 3.10, 3.11, 3.12 | Tested in CI (matrix finalized in ATW-5) |

`min_version = "3.5.0"` is set in `AtwConfig` (`netbox_atw/__init__.py`).

## Installation

```bash
pip install netbox-atw
```

Add the plugin to your NetBox configuration
(`/etc/netbox/configuration.py`):

```python
PLUGINS = [
    "netbox_atw",
]
```

Run database migrations (the plugin ships `0001_initial` for the
`ImportJob` audit model):

```bash
cd /opt/netbox
python manage.py migrate
```

Restart NetBox services:

```bash
sudo systemctl restart netbox netbox-rq
```

> After install on a new NetBox version, run
> `python manage.py makemigrations netbox_atw` to reconcile any
> `NetBoxModel` base-field drift, then commit the generated migration.

## Configuration

No required configuration. Optional `PLUGINS_CONFIG` (no keys yet; reserved
for future import defaults):

```python
PLUGINS_CONFIG = {
    "netbox_atw": {},
}
```

## Usage — bulk import devices

1. Navigate to **Plugins → Atw → New Import** in the NetBox sidebar.
2. Pick a target (today: `device`) and paste your data. The first row must be a
   header. Use names for FK columns:

   ```csv
   Name,Site,Manufacturer,Device Type,Role,Serial
   rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001
   rtr02,AMS01,Cisco,Catalyst 9300,Router,SER002
   sw01,FR01,Juniper,EX4400-48T,Switch,SER003
   ```

3. Click **Preview import**. You get a per-row table showing `create` /
   `update` / `skip` / `error` and any error messages — with **no data
   written**. A dry-run ImportJob is recorded for audit.
4. Review, then click **Commit**. You're redirected to the ImportJob detail
   page showing the committed outcome, per-row detail, and the raw input.

See [docs/bulk-import.md](docs/bulk-import.md) for the full walkthrough and
[docs/examples/](docs/examples/) for worked datasets.

### Audit history

Every run (preview or commit) creates an **ImportJob** visible under
**Plugins → Atw → Import Jobs**, with summary counts, per-row detail, the raw
input, and a timestamp. The same data is available via the REST API:

```bash
curl -s http://netbox/api/plugins/atw/import-jobs/ | jq
```

See [docs/api.md](docs/api.md) for the full API reference.

### Device columns

| Header        | Required | FK resolved by | Notes |
|---------------|----------|----------------|-------|
| Name          | yes      | —              | device name |
| Site          | yes      | `Site.name`    | |
| Manufacturer  | yes      | `Manufacturer.name` | |
| Device Type   | yes      | `DeviceType.model` | |
| Role          | yes      | `DeviceRole.name` | |
| Tenant        | no       | `Tenant.name`  | |
| Platform      | no       | `Platform.name`| |
| Serial        | no       | —              | |
| Asset Tag     | no       | —              | |
| Status        | no       | —              | defaults to `active` |
| Comments      | no       | —              | |

A device is updated (vs created) when an existing device matches the natural
key `name + site`.

## Adding a new importer

The importer framework is model-agnostic. To add a new target, register an
`ImportSpec` in `netbox_atw/import_specs.py`:

```python
from .importer import Column, ImportSpec

MY_SPEC = ImportSpec(
    name="my_thing",
    model="app.Model",
    description="...",
    natural_key=("name",),
    columns=[
        Column(field="name", header="Name", required=True),
        Column(field="site", header="Site", fk_lookup_field="name", fk_model="dcim.Site"),
    ],
)

SPECS["my_thing"] = MY_SPEC
```

It then appears in the wizard's target list automatically. See
[docs/adding-an-importer.md](docs/adding-an-importer.md) for the full guide.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

Quick start:

```bash
git clone https://github.com/openjarv/netbox-atw.git
cd netbox-atw
pip install -e ".[dev]"
black --check . && isort --check-only . && flake8 .
pytest
```

Tests require a NetBox development environment. Unit tests in
`tests/test_importer.py` cover pure-Python parts (no NetBox DB required);
integration tests in `tests/test_importer_integration.py` run against a
NetBox dev instance and exercise the full create/update/skip/error path and
the UI wizard.

## Documentation

- [docs/bulk-import.md](docs/bulk-import.md) — full bulk-import usage guide
- [docs/examples/](docs/examples/) — worked example datasets
- [docs/api.md](docs/api.md) — REST API reference
- [docs/adding-an-importer.md](docs/adding-an-importer.md) — extending the importer
- [docs/RELEASING.md](docs/RELEASING.md) — release runbook
- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community standards

## Support

- Open an issue: https://github.com/openjarv/netbox-atw/issues
- Security reports: see [SECURITY.md](SECURITY.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.