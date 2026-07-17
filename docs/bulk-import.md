# Bulk import usage guide

Goal: populate NetBox devices from a real-world spreadsheet, end to end,
using the Atw bulk import wizard — without writing IDs by hand.

This is the first scenario the plugin ships. The importer framework is
model-agnostic; see [adding-an-importer.md](adding-an-importer.md) for other
targets.

## Prerequisites

- The plugin is installed and `migrate` has been run (see the
  [README](../README.md#installation)).
- NetBox >= 3.5.
- The NetBox records the import references must already exist in NetBox:
  the **Site**, **Manufacturer**, **Device Type**, and **Device Role** you
  name in your data must be present in NetBox. Atw resolves them by name
  (or `model`, for `DeviceType`); it does not create referenced objects.
- Your user has the `netbox_atw.add_importjob` permission for the wizard and
  `dcim.add_device` (and `dcim.change_device`) for the actual writes.

## Inputs

A CSV or TSV with a header row. The first shipped scenario is `device`.
Headers are matched case-insensitively; unknown columns are ignored (with a
warning in the preview), so extra columns in real-world exports do not break
the import.

Example (`docs/examples/devices.csv`):

```csv
Name,Site,Manufacturer,Device Type,Role,Serial
rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001
rtr02,AMS01,Cisco,Catalyst 9300,Router,SER002
sw01,FR01,Juniper,EX4400-48T,Switch,SER003
fw01,FR01,Palo Alto,PA-440,Firewall,SER004
```

### Device columns

| Header        | Required | FK resolved by        | Notes                  |
|---------------|----------|-----------------------|------------------------|
| Name          | yes      | —                     | device name            |
| Site          | yes      | `Site.name`           |                        |
| Manufacturer  | yes      | `Manufacturer.name`   |                        |
| Device Type   | yes      | `DeviceType.model`    | matched on `model`, not name |
| Role          | yes      | `DeviceRole.name`     |                        |
| Tenant        | no       | `Tenant.name`         |                        |
| Platform      | no       | `Platform.name`       |                        |
| Serial        | no       | —                     |                        |
| Asset Tag     | no       | —                     |                        |
| Status        | no       | —                     | defaults to `active`   |
| Comments      | no       | —                     |                        |

### Natural key

A device is **updated** (vs created) when an existing device matches the
natural key `name + site`. Otherwise the row creates a new device.

## Steps

### 1. Open the wizard

Navigate to **Plugins → Atw → New Import** in the NetBox sidebar.

### 2. Pick a target and paste your data

- **Target:** `device`
- **Delimiter:** CSV (comma) or TSV (tab)
- **Data:** paste your rows. The first row must be a header.

### 3. Preview (dry run)

Click **Preview import**. You get a per-row table showing one of:

- `create` — no existing device matches `name + site`; a new device will be
  created.
- `update` — an existing device matches; fields that differ will be updated.
- `skip` — an existing device matches and nothing changed.
- `error` — the row did not validate (missing required field, FK not found,
  etc.). The error message is shown per row.

**No data is written on a preview.** A dry-run `ImportJob` is recorded so the
preview itself is auditable.

### 4. Commit

Review the preview, then click **Commit**. You are redirected to the
ImportJob detail page showing the committed outcome, per-row detail, summary
counts, and the raw input.

## Validation

- **Required columns** must be present and non-empty on every row. Missing
  required columns raise a header error before any row is processed; empty
  required values on a row mark that row `error` and let the rest proceed.
- **FK resolution** is cached per run. If a referenced object does not exist,
  the row is marked `error` with a message like
  `Could not find Site with name='XYZ'`.
- **Model validation** (`full_clean`) runs on every create/update. Django
  validation errors mark the row `error`.
- **Atomicity:** all rows run inside one `transaction.atomic` savepoint.
  Per-row `try/except` means a single bad row does not roll back the good
  ones; the savepoint only rolls back on dry-run.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Could not find Site with name='XYZ'` | The site does not exist in NetBox | Create the site in NetBox first, or fix the name in your data |
| `Could not find DeviceType with model='XYZ'` | Device types are matched on `model`, not the display name | Use the `model` value exactly as it appears in NetBox |
| `Missing required column(s): ...` | A required header is absent from your data | Add the column (empty values are allowed; the row will error instead) |
| Every row `error` with the same message | A common upstream issue (wrong site, wrong model name) | Fix one row, re-preview, confirm, then re-commit |
| Unknown columns ignored | Real-world exports carry extra columns; Atw ignores them | Safe — remove them only if you want a clean preview |

## Audit

Every run — preview or commit — creates an `ImportJob`:

- **UI:** **Plugins → Atw → Import Jobs** lists all jobs; click any job for
  per-row detail, summary counts, the raw input, and a timestamp.
- **REST API:** `GET /api/plugins/atw/import-jobs/` (see [api.md](api.md)).
- **Search:** ImportJob records are indexed in global NetBox search on
  `spec`, `summary`, and `data`.