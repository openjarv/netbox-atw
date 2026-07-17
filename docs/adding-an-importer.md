# Adding a new importer

The importer framework is model-agnostic. A new target is a single
`ImportSpec` — no new views, URLs, or templates.

## Where to add it

Register specs in `netbox_atw/import_specs.py` in the `SPECS` dict. Anything
in `SPECS` appears in the wizard's target list automatically.

## Anatomy of an `ImportSpec`

```python
from .importer import Column, ImportSpec

MY_SPEC = ImportSpec(
    name="my_thing",          # unique key in SPECS; shown in the wizard
    model="app.Model",         # target NetBox model as app_label.ModelName
    description="...",         # shown next to the target in the wizard
    natural_key=("name",),     # fields used for create-vs-update; () = always create
    columns=[
        Column(field="name", header="Name", required=True),
        Column(
            field="site",
            header="Site",
            fk_lookup_field="name",   # resolve the FK by this field on the related model
            fk_model="dcim.Site",     # app_label.ModelName of the related model
        ),
    ],
)

SPECS["my_thing"] = MY_SPEC
```

### `Column`

| Argument             | Type   | Default | Purpose                                                        |
|----------------------|--------|---------|----------------------------------------------------------------|
| `field`              | str    | —       | Target model field name.                                       |
| `header`             | str?   | `None`  | Human-readable header; defaults to a Title-cased `field`.      |
| `required`           | bool   | `False` | Must be present and non-empty on every row.                    |
| `fk_lookup_field`    | str?   | `None`  | If set, the column is a FK resolved by this field.             |
| `fk_model`           | str?   | `None`  | `app_label.ModelName` of the related model (required for FKs). |
| `fk_filterset_kwargs`| dict?  | `None`  | Extra lookup kwargs (e.g. to scope a tenant by group).         |
| `default`            | any    | `None`  | Value used when the column is absent or empty.                |

### `natural_key`

A tuple of model field names used to decide `create` vs `update`.

- If a row matches an existing object on the natural key, the row **updates**
  that object (only changed fields are written) or is **skipped** if nothing
  changed.
- If no object matches, the row **creates** a new object.
- Empty natural key `()` means every row creates a new object (useful for
  models without a natural key).

Natural-key fields declared with a FK column are rewritten to `_id` for the
lookup automatically (e.g. `site` → `site_id`).

## How resolution works

1. **Parse** the pasted text with the chosen delimiter; the first row is the
   header. Blank lines are ignored.
2. **Validate header:** all required columns must be present. Unknown columns
   are returned as a warning, not an error (real-world exports carry extra
   columns).
3. **Per row:**
   - Build field kwargs. FK columns are resolved to the related PK by
     `fk_lookup_field` and stored as `<field>_id`; the FK cache is per-run so
     repeated names cost one query.
   - If a required column is empty, the row is `error`.
   - If `natural_key` matches an existing object: update changed fields, or
     skip if nothing changed.
   - Otherwise: create.
   - `full_clean()` runs on every create/update; Django validation errors
     mark the row `error`.
4. **Atomicity:** all rows run inside one `transaction.atomic` savepoint.
   Per-row `try/except` isolates bad rows so good rows still commit. Dry
   runs raise an internal sentinel that rolls the whole savepoint back —
   previews write nothing.

## Testing your spec

- Add unit tests under `netbox_atw/tests/` mirroring the existing
  `test_import_specs.py` / `test_importer_run.py` style.
- For end-to-end coverage, add an integration test under
  `tests/test_importer_integration.py` that runs against a NetBox dev
  instance.
- Update `docs/bulk-import.md` (or add a new scenario guide) and the README
  feature list in the same PR.

## Checklist before merging a new importer

- [ ] Spec is in `SPECS` with a unique `name`.
- [ ] `natural_key` is correct for the model (or `()` for always-create).
- [ ] Required columns are marked `required=True`.
- [ ] FK columns set `fk_lookup_field` and `fk_model` correctly.
- [ ] Unit + integration tests added.
- [ ] Docs updated (scenario guide + README feature list).
- [ ] CHANGELOG `Added` entry under `Unreleased`.