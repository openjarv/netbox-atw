# REST API reference

The Atw plugin exposes the **ImportJob** audit model over the standard NetBox
REST API. Import itself is driven through the UI wizard today; the API is for
auditing population history.

## Base URL

```
/api/plugins/atw/
```

## ImportJob

### List import jobs

```bash
curl -s "http://netbox/api/plugins/atw/import-jobs/" \
  -H "Authorization: Token $TOKEN" | jq
```

### Filter

Filterable fields: `id`, `spec`, `status`, `dry_run`, `created`.

```bash
# Only commits (not dry runs)
curl -s "http://netbox/api/plugins/atw/import-jobs/?dry_run=false" \
  -H "Authorization: Token $TOKEN" | jq

# Only device imports
curl -s "http://netbox/api/plugins/atw/import-jobs/?spec=device" \
  -H "Authorization: Token $TOKEN" | jq

# Failed jobs only
curl -s "http://netbox/api/plugins/atw/import-jobs/?status=failed" \
  -H "Authorization: Token $TOKEN" | jq
```

### Retrieve one

```bash
curl -s "http://netbox/api/plugins/atw/import-jobs/12/" \
  -H "Authorization: Token $TOKEN" | jq
```

### Fields

| Field           | Type    | Description                                           |
|-----------------|---------|-------------------------------------------------------|
| id              | int     | ImportJob primary key                                 |
| spec            | string  | Import spec name, e.g. `device`                       |
| status          | string  | `pending`, `running`, `completed`, `failed`           |
| dry_run         | bool    | True if this was a preview run with no data written   |
| delimiter       | string  | Column delimiter used (`,` or `\t`)                   |
| data            | string  | Raw pasted input (CSV/TSV) as submitted               |
| summary         | string  | Human-readable summary, e.g. `3 created, 1 updated`  |
| created_count   | int     | Rows that created a new object                        |
| updated_count   | int     | Rows that updated an existing object                  |
| skipped_count   | int     | Rows that matched the natural key with no changes    |
| errored_count   | int     | Rows that failed validation / write                   |
| result          | object  | Per-row result detail (serialised `RowResult` list)   |
| tags            | array   | NetBox tags                                           |
| created         | string  | ISO timestamp                                         |
| last_updated    | string  | ISO timestamp                                         |

### Create / update / delete

The ImportJob model is a standard NetBox model, so POST / PATCH / DELETE
follow NetBox conventions. **Note:** creating an ImportJob via the API does
**not** re-run the import — it only records an audit row. To run an import,
use the UI wizard (see [bulk-import.md](bulk-import.md)).

## GraphQL

The `ImportJob` type is registered with NetBox's GraphQL schema:

```graphql
query {
  importJobList {
    id
    spec
    status
    dryRun
    summary
    createdCount
    updatedCount
    erroredCount
    created
  }
}
```

(GraphQL field names follow NetBox's camelCase convention.)