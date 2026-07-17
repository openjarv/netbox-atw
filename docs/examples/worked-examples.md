# Worked examples

Copy-pasteable datasets for the Atw bulk import wizard. Each example targets
the `device` spec shipped in 0.1.0. See [../bulk-import.md](../bulk-import.md)
for the full walkthrough.

> Prerequisite: the **Site**, **Manufacturer**, **Device Type**, and
> **Device Role** you reference must already exist in NetBox. Atw resolves
> them by name (or `model`, for `DeviceType`); it does not create referenced
> objects.

## Minimal device import

`minimal-devices.csv`:

```csv
Name,Site,Manufacturer,Device Type,Role,Serial
rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001
rtr02,AMS01,Cisco,Catalyst 9300,Router,SER002
sw01,FR01,Juniper,EX4400-48T,Switch,SER003
fw01,FR01,Palo Alto,PA-440,Firewall,SER004
```

- All four rows are `create` on first run (no existing device matches
  `name + site`).
- Re-running the same data after commit produces four `skip` rows (natural
  key matches, nothing changed).
- Changing `Serial` on `rtr01` and re-running produces one `update` and
  three `skip`.

## Device import with optional columns

`devices-with-tenant.csv`:

```csv
Name,Site,Manufacturer,Device Type,Role,Tenant,Platform,Status,Comments
rtr01,AMS01,Cisco,Catalyst 9300,Router,Acme,cisco-ios,active,Edge router AMS01
rtr02,AMS01,Cisco,Catalyst 9300,Router,Acme,cisco-ios,active,Edge router AMS01 (HA peer)
sw01,FR01,Juniper,EX4400-48T,Switch,Acme,junos,active,Access switch FR01
```

- `Tenant` and `Platform` are optional FK columns resolved by name.
- `Status` defaults to `active` if omitted.
- `Comments` is a free-text column.

## Update-only run

To update attributes on devices that already exist, reuse the natural key
(`name + site`) and change the non-key fields:

`devices-status-update.csv`:

```csv
Name,Site,Manufacturer,Device Type,Role,Status
rtr01,AMS01,Cisco,Catalyst 9300,Router,maintenance
rtr02,AMS01,Cisco,Catalyst 9300,Router,maintenance
```

Preview shows two `update` rows; commit sets `status` to `maintenance` on
both devices. Other fields are left untouched because they did not change.

## TSV input

The wizard accepts TSV as well as CSV. Paste with a tab delimiter and choose
**TSV (tab)** in the wizard. Useful when pasting from a spreadsheet that uses
tabs.

## Error isolation

`mixed-with-errors.csv`:

```csv
Name,Site,Manufacturer,Device Type,Role,Serial
rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001
rtr02,NoSuchSite,Cisco,Catalyst 9300,Router,SER002
badrow,AMS01,Cisco,Catalyst 9300,Router,
sw01,FR01,Juniper,EX4400-48T,Switch,SER003
```

Preview result:

- `rtr01` → `create`
- `rtr02` → `error` (`Could not find Site with name='NoSuchSite'`)
- `badrow` → `error` (`Required column 'Serial' is empty.` — only if Serial
  were required; here it is optional, so this row is `create`)
- `sw01` → `create`

On commit, the two `create` rows are written; the `error` rows are reported
with per-row messages and recorded on the ImportJob.