"""Models for the Atw NetBox plugin.

Atw ships a single bookkeeping model, :class:`ImportJob`, that records each
bulk-import run (who, what, how many created/updated/errored). The actual
target objects (devices, sites, etc.) are created in core NetBox models by
the :mod:`netbox_atw.importer`; ImportJob just records the outcome so users
can audit population history without leaving NetBox.
"""

from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel

from .choices import ImportJobStatusChoices


class ImportJob(NetBoxModel):
    """A record of a single Atw bulk-import run.

    One ImportJob is created per import (dry-run or real). ``data`` holds the
    raw pasted input, ``summary`` holds the per-row outcome counts, and
    ``result`` holds the per-row detail (list of dicts) for auditing.
    """

    spec = models.CharField(
        max_length=50,
        help_text="Import spec name, e.g. 'device'.",
    )
    status = models.CharField(
        max_length=30,
        choices=ImportJobStatusChoices,
        default=ImportJobStatusChoices.STATUS_PENDING,
    )
    dry_run = models.BooleanField(
        default=False,
        help_text="True if this was a preview run with no data written.",
    )
    delimiter = models.CharField(
        max_length=4,
        default=",",
        help_text="Column delimiter used for the input data.",
    )
    data = models.TextField(
        blank=True,
        help_text="Raw pasted input (CSV/TSV) as submitted by the user.",
    )
    summary = models.CharField(
        max_length=200,
        blank=True,
        help_text="Human-readable summary, e.g. '3 created, 1 updated, 0 errored'.",
    )
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)
    skipped_count = models.PositiveIntegerField(default=0)
    errored_count = models.PositiveIntegerField(default=0)
    result = models.JSONField(
        blank=True,
        default=dict,
        help_text="Per-row result detail (serialised RowResult list).",
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "Import Job"
        verbose_name_plural = "Import Jobs"

    def __str__(self):
        return f"Import {self.pk} ({self.spec})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_atw:importjob", kwargs={"pk": self.pk})
