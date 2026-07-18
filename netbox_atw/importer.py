"""Bulk import / population tooling for the Atw NetBox plugin.

The importer is model-agnostic and extensible: each :class:`ImportSpec` binds a
target NetBox model to a set of :class:`Column` definitions and (optionally) a
natural key used for create-vs-update decisions. Foreign keys can be resolved
by human-readable name instead of NetBox PK, which is the single biggest
friction point when populating NetBox from real-world data.

Typical flow (mirrors the UI in :mod:`netbox_atw.views`):

    spec = get_import_spec("device")
    result = Importer(spec).run(rows, dry_run=False)

The same :class:`Importer` powers the dry-run preview shown to the user before
any rows are committed, so what the user sees is exactly what will happen.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.db import models, transaction


def _get_model(app_model: str) -> type[models.Model]:
    """Resolve an ``app_label.ModelName`` string to a Django model class."""
    app_label, model_name = app_model.split(".")
    return django_apps.get_model(app_label, model_name)


class ImporterError(Exception):
    """Base class for importer errors."""


class HeaderMismatchError(ImporterError):
    """Raised when the provided header row does not satisfy the spec."""


class UnknownImporterError(ImporterError):
    """Raised when an unknown importer name is requested."""


class _DryRunRollback(Exception):
    """Internal sentinel used to roll back the dry-run savepoint cleanly.

    Raising inside a :func:`transaction.atomic` block rolls the savepoint back
    without surfacing an error to callers. Caught and swallowed in
    :meth:`Importer.run`.
    """


@dataclass(frozen=True)
class Column:
    """A single column mapping for an :class:`ImportSpec`.

    ``field`` is the target model field name. ``header`` is the human-readable
    column header the user supplies in their CSV/TSV data; if omitted it
    defaults to a Title-cased version of ``field``. ``required`` columns must be
    present and non-empty on every row. ``fk_lookup_field`` turns the column
    into a foreign-key-by-name lookup against the related model using that
    field (typically ``"name"``, ``"slug"`` or ``"cid"``). ``choices`` may be a
    queryset used to validate / resolve choice-like string columns.
    """

    field: str
    header: Optional[str] = None
    required: bool = False
    fk_lookup_field: Optional[str] = None
    fk_model: Optional[str] = None
    fk_filterset_kwargs: Optional[dict] = None
    default: Any = None

    def resolved_header(self) -> str:
        return self.header or self.field.replace("_", " ").title()


@dataclass
class ImportSpec:
    """A complete description of how to import one NetBox model.

    ``natural_key`` is the tuple of fields used to decide whether a row creates
    a new object or updates an existing one. If empty, every row creates a new
    object (useful for models without a natural key).
    """

    name: str
    model: str
    columns: list[Column]
    natural_key: tuple[str, ...] = ()
    description: str = ""

    def column_for_header(self, header: str) -> Optional[Column]:
        for col in self.columns:
            if col.resolved_header().lower() == header.strip().lower():
                return col
        return None

    def required_headers(self) -> list[str]:
        return [c.resolved_header() for c in self.columns if c.required]


@dataclass
class RowResult:
    """The outcome of processing a single row."""

    row_number: int
    action: str  # "create" | "update" | "skip" | "error"
    object_repr: str = ""
    object_pk: Optional[int] = None
    errors: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class ImportResult:
    """The aggregate outcome of an :class:`Importer.run` call."""

    dry_run: bool
    rows: list[RowResult] = field(default_factory=list)

    @property
    def created(self) -> int:
        return sum(1 for r in self.rows if r.action == "create")

    @property
    def updated(self) -> int:
        return sum(1 for r in self.rows if r.action == "update")

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.rows if r.action == "skip")

    @property
    def errored(self) -> int:
        return sum(1 for r in self.rows if r.action == "error")

    @property
    def ok(self) -> bool:
        return self.errored == 0

    def summary(self) -> str:
        parts = []
        if self.created:
            parts.append(f"{self.created} created")
        if self.updated:
            parts.append(f"{self.updated} updated")
        if self.skipped:
            parts.append(f"{self.skipped} skipped")
        if self.errored:
            parts.append(f"{self.errored} errored")
        return ", ".join(parts) or "no changes"


def parse_delimited(text: str, delimiter: str = ",") -> tuple[list[str], list[dict]]:
    """Parse a delimited string (CSV/TSV) into a header list and row dicts.

    Blank lines are ignored. Raises :class:`HeaderMismatchError` if no header
    row is present.
    """
    if text is None:
        return [], []
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if reader.fieldnames is None:
        raise HeaderMismatchError("No header row found in input.")
    rows = [{k: (v if v is not None else "") for k, v in row.items()} for row in reader if any(v for v in row.values())]
    return list(reader.fieldnames), rows


class Importer:
    """Runs an :class:`ImportSpec` against a list of row dicts."""

    def __init__(self, spec: ImportSpec):
        self.spec = spec
        self._fk_cache: dict[tuple[str, str], int] = {}

    # ------------------------------------------------------------------ model

    def _model(self) -> type[models.Model]:
        return _get_model(self.spec.model)

    # ----------------------------------------------------------------- header

    def validate_header(self, headers: list[str]) -> list[str]:
        """Validate the supplied headers against the spec.

        Raises :class:`HeaderMismatchError` if any required column is missing.
        Returns the list of unknown headers (real-world data often carries
        extra columns we deliberately ignore).
        """
        missing = [h for h in self.spec.required_headers() if not any(h.lower() == x.strip().lower() for x in headers)]
        if missing:
            raise HeaderMismatchError(
                f"Missing required column(s): {', '.join(missing)}. "
                f"Expected headers: {', '.join(c.resolved_header() for c in self.spec.columns)}"
            )
        unknown = [h for h in headers if self.spec.column_for_header(h) is None and h and not h.isspace()]
        return unknown

    # ----------------------------------------------------------------- values

    def _resolve_fk(self, column: Column, raw_value: str) -> Optional[int]:
        if not raw_value:
            return None
        cache_key = (column.field, raw_value.strip().lower())
        if cache_key in self._fk_cache:
            return self._fk_cache[cache_key]
        related_model = _get_model(column.fk_model)
        lookup = {column.fk_lookup_field: raw_value.strip()}
        if column.fk_filterset_kwargs:
            lookup.update(column.fk_filterset_kwargs)
        try:
            obj = related_model.objects.get(**lookup)
        except related_model.DoesNotExist as exc:
            raise ImporterError(
                f"Could not find {related_model.__name__} with {column.fk_lookup_field}='{raw_value}'"
            ) from exc
        self._fk_cache[cache_key] = obj.pk
        return obj.pk

    def _coerce_value(self, column: Column, raw_value: str) -> Any:
        raw_value = (raw_value or "").strip()
        if column.fk_lookup_field and column.fk_model:
            return self._resolve_fk(column, raw_value)
        if not raw_value:
            return column.default
        return raw_value

    def _build_fields(self, row: dict) -> dict:
        """Map a row dict to model field kwargs.

        Foreign-key columns are resolved to the related PK and stored under the
        ``<field>_id`` attribute (e.g. ``site_id``), which Django accepts both in
        the model constructor and via ``setattr``. Storing the FK instance itself
        would require an extra query and breaks ``setattr`` on the FK descriptor.
        """
        fields: dict[str, Any] = {}
        for header, value in row.items():
            column = self.spec.column_for_header(header)
            if column is None:
                continue
            target = column.field + "_id" if column.fk_lookup_field else column.field
            fields[target] = self._coerce_value(column, value)
        # Apply defaults for required columns absent from the row.
        for column in self.spec.columns:
            target = column.field + "_id" if column.fk_lookup_field else column.field
            if target not in fields and column.default is not None:
                fields[target] = column.default
        return fields

    # --------------------------------------------------------------- natural key

    def _natural_key_lookup(self, fields: dict) -> dict:
        """Build the queryset lookup for the natural key, FK-aware.

        Natural keys are declared using model field names (e.g. ``site``); this
        rewrites them to ``site_id`` when the column is a FK so the lookup matches
        the keys produced by :meth:`_build_fields`.
        """
        lookup = {}
        for key in self.spec.natural_key:
            column = next((c for c in self.spec.columns if c.field == key), None)
            attr = key + "_id" if column and column.fk_lookup_field else key
            lookup[attr] = fields.get(attr)
        return lookup

    def _existing(self, fields: dict) -> Optional[models.Model]:
        if not self.spec.natural_key:
            return None
        lookup = self._natural_key_lookup(fields)
        if any(v is None or v == "" for v in lookup.values()):
            return None
        try:
            return self._model().objects.get(**lookup)
        except self._model().DoesNotExist:
            return None
        except self._model().MultipleObjectsReturned as exc:
            raise ImporterError(
                f"Natural key {self.spec.natural_key} matched multiple {self._model().__name__} objects."
            ) from exc

    # ------------------------------------------------------------------- row

    def _process_row(self, row_number: int, row: dict, dry_run: bool) -> RowResult:
        result = RowResult(row_number=row_number, action="skip", raw=row)
        try:
            fields = self._build_fields(row)
            # Required-field presence check (after building, so defaults apply).
            for column in self.spec.columns:
                target = column.field + "_id" if column.fk_lookup_field else column.field
                if column.required and not str(fields.get(target, "")).strip():
                    raise ImporterError(f"Required column '{column.resolved_header()}' is empty.")

            existing = self._existing(fields)
            model = self._model()

            if existing is not None:
                changed = False
                for k, v in fields.items():
                    if not k.startswith("_") and getattr(existing, k, None) != v:
                        setattr(existing, k, v)
                        changed = True
                result.action = "update" if changed else "skip"
                result.object_pk = existing.pk
                result.object_repr = str(existing)
                if changed and not dry_run:
                    existing.full_clean()
                    existing.save()
            else:
                obj = model(**fields)
                result.action = "create"
                result.object_repr = str(obj) or fields.get("name", f"row {row_number}")
                if not dry_run:
                    obj.full_clean()
                    obj.save()
                    result.object_pk = obj.pk
        except (ImporterError, ValidationError, models.ObjectDoesNotExist) as exc:
            result.action = "error"
            result.errors.append(str(exc))
        return result

    # ------------------------------------------------------------------- run

    def run(self, rows: Iterable[dict], dry_run: bool = False) -> ImportResult:
        """Run the spec against ``rows``.

        All work happens inside a single :func:`transaction.atomic` savepoint.
        Dry runs are rolled back with the :class:`_DryRunRollback` sentinel so
        nothing is ever committed by a preview.
        """
        result = ImportResult(dry_run=dry_run)
        try:
            with transaction.atomic():
                for i, row in enumerate(rows, start=2):  # row 1 is the header
                    result.rows.append(self._process_row(i, row, dry_run))
                if dry_run:
                    raise _DryRunRollback  # controlled rollback
        except _DryRunRollback:
            pass
        return result

    def run_text(self, text: str, delimiter: str = ",", dry_run: bool = False) -> ImportResult:
        headers, rows = parse_delimited(text, delimiter=delimiter)
        self.validate_header(headers)
        return self.run(rows, dry_run=dry_run)
