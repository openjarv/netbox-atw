"""pytest configuration for netbox_atw tests.

Two modes:

1. **Inside NetBox** (integration / model / view / API tests): when ``netbox``
   is importable we defer to NetBox's own Django settings via
   ``DJANGO_SETTINGS_MODULE=netbox.settings``. The NetBox dev container sets
   this up through ``manage.py``; we just make sure pytest-django picks it up.

2. **Outside NetBox** (pure-Python importer tests): configure a minimal Django
   settings (in-memory SQLite + the fake test app) so the importer's DB-backed
   logic in ``test_importer_run.py`` can run without a full NetBox dev instance.
   The NetBox-dependent test files skip themselves via ``pytest.importorskip``.

This dual-mode setup lets the same test tree run fast anywhere (laptop, CI unit
job) and fully inside a NetBox dev container.
"""

import os

import django
from django.conf import settings


def _netbox_available() -> bool:
    try:
        import netbox  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


def _configure_minimal():
    """Minimal Django config for pure-Python tests (no NetBox installed)."""
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


def _configure_netbox():
    """Use NetBox's own settings when running inside a NetBox environment."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netbox.settings")
    if not settings.configured:
        django.setup()


if _netbox_available():
    _configure_netbox()
else:
    _configure_minimal()
