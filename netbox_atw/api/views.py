from netbox.api.viewsets import NetBoxModelViewSet

from netbox_atw.filtersets import ImportJobFilterSet
from netbox_atw.models import ImportJob

from .serializers import ImportJobSerializer


class ImportJobViewSet(NetBoxModelViewSet):
    """API viewset for the ImportJob model."""

    queryset = ImportJob.objects.all()
    serializer_class = ImportJobSerializer
    filterset_class = ImportJobFilterSet
