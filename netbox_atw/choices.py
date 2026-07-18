"""Choice sets for the Atw NetBox plugin."""

from django.db import models


class ImportJobStatusChoices(models.TextChoices):
    STATUS_PENDING = "pending", "Pending"
    STATUS_RUNNING = "running", "Running"
    STATUS_COMPLETED = "completed", "Completed"
    STATUS_FAILED = "failed", "Failed"
