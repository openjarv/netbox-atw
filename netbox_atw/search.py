from netbox.search import SearchIndex, register_search

from .models import ImportJob


@register_search
class ImportJobIndex(SearchIndex):
    model = ImportJob
    fields = (
        ("spec", 100),
        ("summary", 300),
        ("data", 500),
    )
