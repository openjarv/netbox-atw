"""DB-backed functional tests for the importer that do NOT require NetBox.

These run against an in-memory SQLite database with a tiny local Django app and
model, exercising the full :meth:`Importer.run` create/update/skip/error path
including dry-run rollback and per-row error isolation — the core logic of
ATW-4 — without standing up a full NetBox development instance.

Django is configured by ``conftest.py`` at the repo root. The integration tests
in :mod:`netbox_atw.tests.test_importer_integration` cover the same path against
the real NetBox Device model and the UI wizard.
"""

from django.db import connection
from django.test import TransactionTestCase

from netbox_atw.importer import Column, Importer, ImportSpec


class ImporterRunTest(TransactionTestCase):
    """End-to-end Importer.run against a real (SQLite) Django model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from netbox_atw.tests._fakemodel.models import FakeDevice, FakeSite

        cls.FakeDevice = FakeDevice
        cls.FakeSite = FakeSite
        # The fake test app's tables are not managed by Django migrations, so
        # create them explicitly if missing (idempotent: the in-memory SQLite
        # connection may already have been set up by pytest-django or a prior
        # test class reusing the same connection).
        cls._created = [FakeSite, FakeDevice]
        existing = set(connection.introspection.table_names())
        with connection.schema_editor() as schema:
            for model in cls._created:
                if model._meta.db_table not in existing:
                    schema.create_model(model)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema:
            for model in reversed(cls._created):
                try:
                    schema.delete_model(model)
                except Exception:
                    pass
        super().tearDownClass()

    def setUp(self):
        self.FakeSite.objects.create(name="AMS01")
        self.spec = ImportSpec(
            name="fakedevice",
            model="tests_fake.FakeDevice",
            description="test",
            natural_key=("name",),
            columns=[
                Column(field="name", header="Name", required=True),
                Column(field="site", header="Site", fk_lookup_field="name", fk_model="tests_fake.FakeSite"),
                Column(field="serial", header="Serial"),
                Column(field="status", header="Status", default="active"),
            ],
        )

    def test_create_resolves_fk_by_name(self):
        result = Importer(self.spec).run_text("Name,Site,Serial\nrtr01,AMS01,SER1", dry_run=False)
        self.assertTrue(result.ok, [r.errors for r in result.rows])
        self.assertEqual(result.created, 1)
        dev = self.FakeDevice.objects.get(name="rtr01")
        self.assertEqual(dev.serial, "SER1")
        self.assertEqual(dev.status, "active")
        self.assertEqual(dev.site.name, "AMS01")

    def test_dry_run_persists_nothing(self):
        result = Importer(self.spec).run_text("Name,Site,Serial\nrtr-dry,AMS01,SER0", dry_run=True)
        self.assertTrue(result.dry_run)
        self.assertEqual(result.created, 1)
        self.assertFalse(self.FakeDevice.objects.filter(name="rtr-dry").exists())

    def test_update_by_natural_key(self):
        Importer(self.spec).run_text("Name,Site,Serial\nrtr01,AMS01,SER1", dry_run=False)
        result = Importer(self.spec).run_text("Name,Site,Serial\nrtr01,AMS01,SER2", dry_run=False)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.created, 0)
        self.assertEqual(self.FakeDevice.objects.get(name="rtr01").serial, "SER2")

    def test_skip_when_unchanged(self):
        csv = "Name,Site,Serial\nrtr01,AMS01,SER1"
        Importer(self.spec).run_text(csv, dry_run=False)
        result = Importer(self.spec).run_text(csv, dry_run=False)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.updated, 0)

    def test_unknown_fk_errors_row_only(self):
        csv = "Name,Site,Serial\nrtr01,AMS01,SER1\nrtr02,NoSuchSite,SER2"
        result = Importer(self.spec).run_text(csv, dry_run=False)
        self.assertEqual(result.created, 1)
        self.assertEqual(result.errored, 1)
        self.assertTrue(self.FakeDevice.objects.filter(name="rtr01").exists())
        self.assertFalse(self.FakeDevice.objects.filter(name="rtr02").exists())


if __name__ == "__main__":
    import unittest

    unittest.main()
