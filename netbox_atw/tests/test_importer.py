"""Tests for :mod:`netbox_atw.importer` that need no Django models.

These tests exercise the pure-Python parts of the importer (parsing, header
validation, result bookkeeping) and run both inside and outside a NetBox test
environment because they never touch the database.
"""

from django.test import SimpleTestCase

from netbox_atw.importer import Column, HeaderMismatchError, ImportResult, ImportSpec, parse_delimited


class ParseDelimitedTest(SimpleTestCase):
    def test_parse_csv(self):
        headers, rows = parse_delimited("Name,Site\nrtr01,AMS01\nrtr02,AMS02")
        self.assertEqual(headers, ["Name", "Site"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Name"], "rtr01")
        self.assertEqual(rows[1]["Site"], "AMS02")

    def test_parse_tsv(self):
        headers, rows = parse_delimited("Name\tSite\nrtr01\tAMS01", delimiter="\t")
        self.assertEqual(headers, ["Name", "Site"])
        self.assertEqual(rows[0]["Site"], "AMS01")

    def test_blank_lines_ignored(self):
        headers, rows = parse_delimited("Name,Site\n\nrtr01,AMS01\n")
        self.assertEqual(len(rows), 1)

    def test_missing_header_raises(self):
        with self.assertRaises(HeaderMismatchError):
            parse_delimited("")

    def test_none_input_returns_empty(self):
        headers, rows = parse_delimited(None)
        self.assertEqual(headers, [])
        self.assertEqual(rows, [])


class ImportResultTest(SimpleTestCase):
    def test_counts_and_summary(self):
        from netbox_atw.importer import RowResult

        result = ImportResult(
            dry_run=True,
            rows=[
                RowResult(row_number=2, action="create"),
                RowResult(row_number=3, action="create"),
                RowResult(row_number=4, action="update"),
                RowResult(row_number=5, action="skip"),
                RowResult(row_number=6, action="error", errors=["boom"]),
            ],
        )
        self.assertEqual(result.created, 2)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.errored, 1)
        self.assertFalse(result.ok)
        self.assertEqual(result.summary(), "2 created, 1 updated, 1 skipped, 1 errored")

    def test_empty_summary(self):
        result = ImportResult(dry_run=True)
        self.assertEqual(result.summary(), "no changes")
        self.assertTrue(result.ok)


class ColumnTest(SimpleTestCase):
    def test_resolved_header_explicit(self):
        col = Column(field="site", header="Site", required=True)
        self.assertEqual(col.resolved_header(), "Site")

    def test_resolved_header_default_title_case(self):
        col = Column(field="asset_tag")
        self.assertEqual(col.resolved_header(), "Asset Tag")


class ImportSpecTest(SimpleTestCase):
    def test_column_for_header_case_insensitive(self):
        spec = ImportSpec(
            name="device",
            model="dcim.Device",
            columns=[Column(field="name", header="Name", required=True)],
        )
        self.assertIsNotNone(spec.column_for_header("name"))
        self.assertIsNotNone(spec.column_for_header(" NAME "))
        self.assertIsNone(spec.column_for_header("missing"))

    def test_required_headers(self):
        spec = ImportSpec(
            name="device",
            model="dcim.Device",
            columns=[
                Column(field="name", header="Name", required=True),
                Column(field="site", header="Site", required=True),
                Column(field="serial", header="Serial"),
            ],
        )
        self.assertEqual(spec.required_headers(), ["Name", "Site"])
