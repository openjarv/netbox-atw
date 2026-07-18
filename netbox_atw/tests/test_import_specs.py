"""Tests for :mod:`netbox_atw.import_specs`.

Pure-Python: asserts the device import spec is wired correctly. Runs both
inside and outside a NetBox test environment.
"""

from django.test import SimpleTestCase

from netbox_atw.import_specs import SPECS, available_specs, get_import_spec


class ImportSpecsTest(SimpleTestCase):
    def test_device_spec_present(self):
        names = [s.name for s in available_specs()]
        self.assertIn("device", names)

    def test_get_import_spec_known(self):
        spec = get_import_spec("device")
        self.assertEqual(spec.name, "device")
        self.assertEqual(spec.model, "dcim.Device")
        self.assertEqual(spec.natural_key, ("name", "site"))

    def test_get_import_spec_unknown_raises(self):
        with self.assertRaises(Exception):
            get_import_spec("does-not-exist")

    def test_device_spec_uses_role_not_device_role(self):
        """The NetBox Device model field is `role`, not `device_role`."""
        spec = get_import_spec("device")
        field_names = [c.field for c in spec.columns]
        self.assertIn("role", field_names)
        self.assertNotIn("device_role", field_names)

    def test_device_spec_fk_targets(self):
        spec = get_import_spec("device")
        fk_models = {c.field: c.fk_model for c in spec.columns if c.fk_model}
        self.assertEqual(fk_models["site"], "dcim.Site")
        self.assertEqual(fk_models["manufacturer"], "dcim.Manufacturer")
        self.assertEqual(fk_models["device_type"], "dcim.DeviceType")
        self.assertEqual(fk_models["role"], "dcim.DeviceRole")
        self.assertEqual(fk_models["tenant"], "tenancy.Tenant")
        self.assertEqual(fk_models["platform"], "dcim.Platform")

    def test_specs_dict_keyed_by_name(self):
        self.assertIn("device", SPECS)
        self.assertIs(SPECS["device"], get_import_spec("device"))
