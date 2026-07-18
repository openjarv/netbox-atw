"""Tests for :class:`netbox_atw.models.ImportJob`.

Requires a running NetBox/Django test database. Skipped when NetBox is not
importable so CI can still run the pure-Python tests in matrix jobs that don't
stand up NetBox.
"""

import pytest

pytest.importorskip("netbox")

from django.test import TestCase

from netbox_atw.choices import ImportJobStatusChoices
from netbox_atw.models import ImportJob


class ImportJobModelTest(TestCase):
    def test_create_import_job(self):
        job = ImportJob.objects.create(
            spec="device",
            status=ImportJobStatusChoices.STATUS_COMPLETED,
            dry_run=True,
            summary="1 created",
            created_count=1,
        )
        self.assertIsNotNone(job.pk)
        self.assertEqual(job.spec, "device")
        self.assertEqual(job.status, ImportJobStatusChoices.STATUS_COMPLETED)
        self.assertTrue(job.dry_run)

    def test_str_representation(self):
        job = ImportJob.objects.create(spec="device")
        self.assertEqual(str(job), f"Import {job.pk} (device)")

    def test_default_status_is_pending(self):
        job = ImportJob.objects.create(spec="device")
        self.assertEqual(job.status, ImportJobStatusChoices.STATUS_PENDING)

    def test_default_counts_zero(self):
        job = ImportJob.objects.create(spec="device")
        self.assertEqual(job.created_count, 0)
        self.assertEqual(job.updated_count, 0)
        self.assertEqual(job.skipped_count, 0)
        self.assertEqual(job.errored_count, 0)

    def test_result_json_default_empty_dict(self):
        job = ImportJob.objects.create(spec="device")
        self.assertEqual(job.result, {})

    def test_ordering_newest_first(self):
        first = ImportJob.objects.create(spec="device")
        second = ImportJob.objects.create(spec="device")
        qs = ImportJob.objects.all()
        self.assertEqual(qs[0], second)
        self.assertEqual(qs[1], first)
