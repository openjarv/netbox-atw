"""REST API tests for the ImportJob model.

Requires a running NetBox/Django test database. Skipped when NetBox is not
importable.
"""

import pytest

pytest.importorskip("netbox")

from django.test import TestCase
from rest_framework import status

from netbox_atw.choices import ImportJobStatusChoices
from netbox_atw.models import ImportJob


class ImportJobAPITest(TestCase):
    def test_list_import_jobs(self):
        url = "/api/plugins/atw/import-jobs/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_import_job(self):
        url = "/api/plugins/atw/import-jobs/"
        data = {
            "spec": "device",
            "status": ImportJobStatusChoices.STATUS_COMPLETED,
            "dry_run": True,
            "delimiter": ",",
            "data": "Name,Site\nrtr01,AMS01",
            "summary": "1 created",
            "created_count": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ImportJob.objects.filter(spec="device").count(), 1)

    def test_retrieve_import_job(self):
        job = ImportJob.objects.create(spec="device", summary="1 created")
        url = f"/api/plugins/atw/import-jobs/{job.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["spec"], "device")

    def test_delete_import_job(self):
        job = ImportJob.objects.create(spec="device")
        pk = job.pk
        url = f"/api/plugins/atw/import-jobs/{pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ImportJob.objects.filter(pk=pk).exists())
