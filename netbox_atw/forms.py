from django import forms

from netbox_atw.choices import ImportJobStatusChoices
from netbox_atw.models import ImportJob

from .import_specs import available_specs

DELIMITER_CHOICES = (
    (",", "CSV (comma)"),
    ("\t", "TSV (tab)"),
)


class ImportJobForm(forms.ModelForm):
    """Form for creating/editing ImportJob objects directly (admin/edit view)."""

    class Meta:
        model = ImportJob
        fields = [
            "spec",
            "status",
            "dry_run",
            "delimiter",
            "data",
            "summary",
            "created_count",
            "updated_count",
            "skipped_count",
            "errored_count",
            "tags",
        ]


class ImportJobFilterForm(forms.Form):
    """Filter form for the ImportJob list view."""

    model = ImportJob

    q = forms.CharField(required=False, label="Search")
    spec = forms.ChoiceField(required=False, choices=[("", "---------")])
    status = forms.ChoiceField(
        required=False,
        choices=[("", "---------")] + ImportJobStatusChoices.choices,
    )
    dry_run = forms.NullBooleanField(required=False)


class ImportStartForm(forms.Form):
    """Step 1: pick a target model and paste data."""

    spec = forms.ChoiceField(
        label="Target",
        help_text="Which NetBox object type to populate.",
    )
    data = forms.CharField(
        label="Data",
        widget=forms.Textarea(
            attrs={
                "rows": 14,
                "placeholder": (
                    "Name,Site,Manufacturer,Device Type,Role,Serial\n" "rtr01,AMS01,Cisco,Catalyst 9300,Router,ABC123"
                ),
            }
        ),
        help_text="First row must be a header. FK columns use names, not IDs.",
    )
    delimiter = forms.ChoiceField(
        choices=DELIMITER_CHOICES,
        initial=",",
        help_text="Column delimiter for the pasted data.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["spec"].choices = [(s.name, f"{s.name} — {s.description}") for s in available_specs()]


class ImportConfirmForm(forms.Form):
    """Step 2: confirm after reviewing the dry-run preview.

    ``dry_run`` is hidden and sent as a falsey value by the confirm template's
    commit button so the confirm view runs a real import. The start view sends
    ``dry_run=True`` to keep the preview auditable without committing.
    """

    spec = forms.CharField(widget=forms.HiddenInput)
    data = forms.CharField(widget=forms.HiddenInput)
    delimiter = forms.CharField(widget=forms.HiddenInput)
    dry_run = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.HiddenInput,
        help_text="If checked, no data is written.",
    )

    def clean_dry_run(self):
        # BooleanField.clean returns the parsed bool; honor it as-is so the
        # confirm template can send dry_run=False (or omit it) to commit.
        return self.cleaned_data.get("dry_run", False)
