# netbox-atw

An [Atw](https://github.com/openjarv/netbox-atw) [NetBox](https://netbox.dev) plugin that reduces the friction of populating NetBox from real-world data.

## What it does

Real-world NetBox data lives in spreadsheets: device lists from a refresh audit, site sheets from facilities, vendor BOMs. Pasting that into NetBox is friction-heavy because the native UI wants primary keys, not names, and there's no preview before commit.

`netbox-atw` ships a two-step bulk-import wizard:

1. **Paste** CSV/TSV data and pick a target object type (device, site, ...).
2. **Preview** a dry-run that shows exactly what will be created, updated, skipped, or errored — foreign keys resolved by **name**, not NetBox PK.
3. **Commit** once the preview looks right.

The first shipped importer is **Device** population, one of the most common and highest-friction real-world tasks (devices reference manufacturer, device type, site, role, tenant, platform — all by name in spreadsheets, by PK in NetBox).

## Compatibility matrix

| netbox-atw | NetBox | Python |
|-----------|--------|--------|
| 0.1.x     | 4.6.x  | 3.10, 3.11, 3.12 |

The plugin targets NetBox 4.6+ (current: 4.6.5). Broader 4.x support will be added as the test matrix expands; we do not cut the compatibility matrix without CEO sign-off.

## Installation

```bash
pip install netbox-atw
```

Add the plugin to your NetBox configuration (`/etc/netbox/configuration.py`):

```python
PLUGINS = [
    "netbox_atw",
]

PLUGINS_CONFIG = {
    "netbox_atw": {
        # No required configuration for 0.1.0
    },
}
```

Run database migrations and restart NetBox:

```bash
cd /opt/netbox
python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

## Usage

1. Navigate to **Plugins → New Import** in the NetBox sidebar.
2. Pick a target (e.g. `device`), paste CSV/TSV data, choose a delimiter.
3. Review the dry-run preview (created / updated / skipped / errored per row).
4. Click **Commit Import** to write the data.
5. Audit past runs under **Plugins → Import Jobs**.

### Device import columns

| Header        | Required | FK lookup     |
|---------------|----------|---------------|
| Name          | yes      | —             |
| Site          | yes      | `dcim.Site.name` |
| Manufacturer  | yes      | `dcim.Manufacturer.name` |
| Device Type   | yes      | `dcim.DeviceType.model` |
| Role          | yes      | `dcim.DeviceRole.name` |
| Tenant        | no       | `tenancy.Tenant.name` |
| Platform      | no       | `dcim.Platform.name` |
| Serial        | no       | —             |
| Asset Tag     | no       | —             |
| Status        | no       | — (default: `active`) |
| Comments      | no       | —             |

Example:

```csv
Name,Site,Manufacturer,Device Type,Role,Serial
rtr01,AMS01,Cisco,Catalyst 9300,Router,ABC123
rtr02,AMS02,Juniper,EX4400,Router,DEF456
```

## Architecture

- `netbox_atw/importer.py` — model-agnostic import engine (`ImportSpec`, `Column`, `Importer`, dry-run with savepoint rollback).
- `netbox_atw/import_specs.py` — concrete specs per target model. Add a new importer by registering an `ImportSpec`.
- `netbox_atw/models.py` — `ImportJob` bookkeeping model (audits every import run).
- `netbox_atw/views.py` — standard CRUD for `ImportJob` + two-step import wizard.
- `netbox_atw/api/` — REST API for `ImportJob`.
- `netbox_atw/graphql/` — GraphQL type for `ImportJob`.
- `netbox_atw/templates/netbox_atw/` — UI templates for the wizard and detail view.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for local dev setup, tests, and the compatibility matrix.

## License

Apache-2.0