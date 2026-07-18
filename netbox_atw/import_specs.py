"""Concrete import specs for the Atw plugin.

A spec binds a NetBox model to a set of column mappings. New importers are
added to :data:`SPECS`. The first shipped scenario is Device population, which
is one of the most common and highest-friction real-world data entry tasks in
NetBox (devices reference manufacturer, device_type, site, role and tenant —
all by name in real-world spreadsheets, but by PK in the NetBox UI).
"""

from .importer import Column, ImportSpec

DEVICE_IMPORT_SPEC = ImportSpec(
    name="device",
    model="dcim.Device",
    description="Populate NetBox devices from a CSV/TSV with FKs resolved by name.",
    natural_key=("name", "site"),
    columns=[
        Column(field="name", header="Name", required=True),
        Column(
            field="site",
            header="Site",
            required=True,
            fk_lookup_field="name",
            fk_model="dcim.Site",
        ),
        Column(
            field="manufacturer",
            header="Manufacturer",
            required=True,
            fk_lookup_field="name",
            fk_model="dcim.Manufacturer",
        ),
        Column(
            field="device_type",
            header="Device Type",
            required=True,
            fk_lookup_field="model",
            fk_model="dcim.DeviceType",
        ),
        Column(
            field="role",
            header="Role",
            required=True,
            fk_lookup_field="name",
            fk_model="dcim.DeviceRole",
        ),
        Column(
            field="tenant",
            header="Tenant",
            fk_lookup_field="name",
            fk_model="tenancy.Tenant",
        ),
        Column(
            field="platform",
            header="Platform",
            fk_lookup_field="name",
            fk_model="dcim.Platform",
        ),
        Column(field="serial", header="Serial"),
        Column(field="asset_tag", header="Asset Tag"),
        Column(field="status", header="Status", default="active"),
        Column(field="comments", header="Comments"),
    ],
)

SPECS: dict[str, ImportSpec] = {
    DEVICE_IMPORT_SPEC.name: DEVICE_IMPORT_SPEC,
}


def get_import_spec(name: str) -> ImportSpec:
    from .importer import UnknownImporterError

    spec = SPECS.get(name)
    if spec is None:
        raise UnknownImporterError(f"Unknown importer '{name}'. Available: {', '.join(sorted(SPECS))}")
    return spec


def available_specs() -> list[ImportSpec]:
    return list(SPECS.values())
