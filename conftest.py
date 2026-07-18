"""pytest configuration for netbox_atw unit tests.

Configures a minimal Django setup (in-memory SQLite + the fake test app) so
the importer's DB-backed logic can be exercised without a full NetBox dev
instance. Integration tests that require NetBox live in
``test_importer_integration.py`` and are skipped automatically when NetBox is
not importable.
"""

import django
from django.conf import settings


def _configure():
    if settings.configured:
        return
    settings.configure(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "netbox_atw.tests._fakemodel",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=True,
    )
    django.setup()


_configure()