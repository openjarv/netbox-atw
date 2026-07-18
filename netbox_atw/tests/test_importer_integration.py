"""Integration tests for the Atw bulk import workflow against a NetBox dev instance.

These tests require a running NetBox development database (the standard NetBox
test settings). They cover the real create/update/skip/error end-to-end path of
the :class:`Importer` and the two-step UI wizard, including foreign-key
resolution by name — the core friction-reducing behavior of the device importer.

Skipped automatically when NetBox is not importable.
"""

import pytest

pytest.importorskip("netbox")

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from django.test import TestCase
from django.urls import reverse

from netbox_atw.import_specs import get_import_spec
from netbox_atw.importer import HeaderMismatchError, Importer

DEVICE_SPEC = get_import_spec("device")


class DeviceImportTestCase(TestCase):
    """Base class that seeds the FK targets devices reference by name."""

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name="AMS01", slug="ams01")
        cls.manufacturer = Manufacturer.objects.create(name="Cisco", slug="cisco")
        cls.device_type = DeviceType.objects.create(
            model="Catalyst 9300",
            slug="catalyst-9300",
            manufacturer=cls.manufacturer,
        )
        cls.role = DeviceRole.objects.create(name="Router", slug="router")

    def _csv(self, rows: str) -> str:
        header = "Name,Site,Manufacturer,Device Type,Role,Serial"
        return header + "\n" + rows


class ImporterCreateTest(DeviceImportTestCase):
    def test_create_single_device_by_name(self):
        csv = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001")
        result = Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        self.assertTrue(result.ok, result.rows)
        self.assertEqual(result.created, 1)
        dev = Device.objects.get(name="rtr01")
        self.assertEqual(dev.site, self.site)
        self.assertEqual(dev.device_type, self.device_type)
        self.assertEqual(dev.role, self.role)
        self.assertEqual(dev.serial, "SER001")

    def test_create_multiple_devices(self):
        csv = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001\nrtr02,AMS01,Cisco,Catalyst 9300,Router,SER002")
        result = Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        self.assertEqual(result.created, 2)
        self.assertEqual(Device.objects.filter(name__in=["rtr01", "rtr02"]).count(), 2)

    def test_dry_run_creates_nothing(self):
        csv = self._csv("rtr-dry,AMS01,Cisco,Catalyst 9300,Router,SER000")
        result = Importer(DEVICE_SPEC).run_text(csv, dry_run=True)
        self.assertTrue(result.dry_run)
        self.assertEqual(result.created, 1)
        self.assertFalse(Device.objects.filter(name="rtr-dry").exists())


class ImporterUpdateTest(DeviceImportTestCase):
    def test_update_existing_by_natural_key(self):
        csv = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001")
        Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        # Change serial only.
        csv2 = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER999")
        result = Importer(DEVICE_SPEC).run_text(csv2, dry_run=False)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.created, 0)
        dev = Device.objects.get(name="rtr01")
        self.assertEqual(dev.serial, "SER999")

    def test_skip_when_unchanged(self):
        csv = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001")
        Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        result = Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.updated, 0)


class ImporterErrorTest(DeviceImportTestCase):
    def test_unknown_fk_errors_row(self):
        csv = self._csv("rtr01,NoSuchSite,Cisco,Catalyst 9300,Router,SER001")
        result = Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        self.assertEqual(result.errored, 1)
        self.assertIn("NoSuchSite", result.rows[0].errors[0])
        self.assertFalse(Device.objects.filter(name="rtr01").exists())

    def test_missing_required_header_raises(self):
        csv = "Name,Site\nrtr01,AMS01"
        with self.assertRaises(HeaderMismatchError):
            Importer(DEVICE_SPEC).run_text(csv, dry_run=False)

    def test_partial_failure_rolls_back_on_error_only(self):
        # First row valid, second row FK error. Atomic block means the errored
        # row is not persisted; the valid row is committed (errors are caught
        # per-row inside the outer transaction).
        csv = self._csv(
            "rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001\nrtr02,BadSite,Cisco,Catalyst 9300,Router,SER002"
        )
        result = Importer(DEVICE_SPEC).run_text(csv, dry_run=False)
        self.assertEqual(result.created, 1)
        self.assertEqual(result.errored, 1)
        self.assertTrue(Device.objects.filter(name="rtr01").exists())
        self.assertFalse(Device.objects.filter(name="rtr02").exists())


class ImportWizardViewTest(DeviceImportTestCase):
    def test_import_home_view(self):
        response = self.client.get(reverse("plugins:netbox_atw:import_home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bulk Import")

    def test_import_start_view_get(self):
        response = self.client.get(reverse("plugins:netbox_atw:import_start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paste your data")

    def test_import_start_preview_post(self):
        csv = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001")
        response = self.client.post(
            reverse("plugins:netbox_atw:import_start"),
            {"spec": "device", "data": csv, "delimiter": ","},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dry-run preview")
        self.assertContains(response, "rtr01")

    def test_import_confirm_post_creates_device(self):
        from netbox_atw.models import ImportJob

        csv = self._csv("rtr01,AMS01,Cisco,Catalyst 9300,Router,SER001")
        # Confirm sends a falsey/absent dry_run so the confirm view commits.
        response = self.client.post(
            reverse("plugins:netbox_atw:import_confirm"),
            {"spec": "device", "data": csv, "delimiter": ","},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Device.objects.filter(name="rtr01", serial="SER001").exists())
        # An ImportJob audit record should exist for the committed run.
        self.assertTrue(ImportJob.objects.filter(spec="device", dry_run=False).exists())

    def test_import_confirm_dry_run_creates_no_device(self):
        from netbox_atw.models import ImportJob

        csv = self._csv("rtr-dry,AMS01,Cisco,Catalyst 9300,Router,SER000")
        response = self.client.post(
            reverse("plugins:netbox_atw:import_confirm"),
            {"spec": "device", "data": csv, "delimiter": ",", "dry_run": "on"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Device.objects.filter(name="rtr-dry").exists())
        self.assertTrue(ImportJob.objects.filter(spec="device", dry_run=True).exists())
