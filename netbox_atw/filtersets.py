from netbox.filtersets import NetBoxModelFilterSet

from .models import ImportJob


class ImportJobFilterSet(NetBoxModelFilterSet):
    """FilterSet for the ImportJob model."""

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "spec",
            "status",
            "dry_run",
            "created",
        ]
