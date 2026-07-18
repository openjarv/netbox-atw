from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ImportJob",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    "spec",
                    models.CharField(help_text="Import spec name, e.g. 'device'.", max_length=50),
                ),
                (
                    "status",
                    models.CharField(
                        default="pending",
                        max_length=30,
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                    ),
                ),
                (
                    "dry_run",
                    models.BooleanField(
                        default=False,
                        help_text="True if this was a preview run with no data written.",
                    ),
                ),
                (
                    "delimiter",
                    models.CharField(default=",", help_text="Column delimiter used for the input data.", max_length=4),
                ),
                (
                    "data",
                    models.TextField(
                        blank=True,
                        help_text="Raw pasted input (CSV/TSV) as submitted by the user.",
                    ),
                ),
                (
                    "summary",
                    models.CharField(
                        blank=True,
                        help_text="Human-readable summary, e.g. '3 created, 1 updated, 0 errored'.",
                        max_length=200,
                    ),
                ),
                ("created_count", models.PositiveIntegerField(default=0)),
                ("updated_count", models.PositiveIntegerField(default=0)),
                ("skipped_count", models.PositiveIntegerField(default=0)),
                ("errored_count", models.PositiveIntegerField(default=0)),
                (
                    "result",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Per-row result detail (serialised RowResult list).",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(related_name="extras_tag_netbox_atw_importjob", to="extras.tag", blank=True),
                ),
            ],
            options={
                "verbose_name": "Import Job",
                "verbose_name_plural": "Import Jobs",
                "ordering": ["-created"],
            },
        ),
    ]
