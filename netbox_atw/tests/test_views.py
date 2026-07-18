"""View tests for the ImportJob list/detail pages.

Requires a running NetBox/Django test database. Skipped when NetBox is not
importable.
"""

import pytest

pytest.importorskip("netbox")

from django.test import TestCase
from django.urls import reverse

from netbox_atw.models import ImportJob


class ImportJobViewTest(TestCase):
    def test_list_view(self):
        url = reverse("plugins:netbox_atw:importjob_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view_with_data(self):
        job = ImportJob.objects.create(spec="device", summary="1 created")
        url = reverse("plugins:netbox_atw:importjob_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(job))

    def test_detail_view(self):
        job = ImportJob.objects.create(spec="device", summary="1 created")
        url = reverse("plugins:netbox_atw:importjob", kwargs={"pk": job.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "device")
