import django_tables2 as tables
from netbox.tables import NetBoxTable

from .models import ImportJob


class ImportJobTable(NetBoxTable):
    """Table configuration for the ImportJob list view."""

    id = tables.LinkColumn()
    spec = tables.Column()
    status = tables.Column()
    dry_run = tables.BooleanColumn()
    summary = tables.Column()
    created_count = tables.Column()
    updated_count = tables.Column()
    errored_count = tables.Column()
    created = tables.DateTimeColumn()

    class Meta(NetBoxTable.Meta):
        model = ImportJob
        fields = (
            "id",
            "spec",
            "status",
            "dry_run",
            "summary",
            "created_count",
            "updated_count",
            "skipped_count",
            "errored_count",
            "created",
        )
        default_columns = (
            "id",
            "spec",
            "status",
            "dry_run",
            "summary",
            "created_count",
            "updated_count",
            "errored_count",
            "created",
        )
