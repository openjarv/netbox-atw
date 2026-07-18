from netbox.graphql.types import NetBoxObjectType

from netbox_atw.models import ImportJob


class ImportJobType(NetBoxObjectType):
    class Meta:
        model = ImportJob
        fields = "__all__"


class Query:
    pass
