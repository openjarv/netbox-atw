from netbox.api.serializers import NetBoxModelSerializer

from netbox_atw.models import ImportJob


class ImportJobSerializer(NetBoxModelSerializer):
    """Serializer for the ImportJob model."""

    class Meta:
        model = ImportJob
        fields = [
            "id",
            "spec",
            "status",
            "dry_run",
            "delimiter",
            "data",
            "summary",
            "created_count",
            "updated_count",
            "skipped_count",
            "errored_count",
            "result",
            "tags",
            "created",
            "last_updated",
        ]
