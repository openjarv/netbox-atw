"""Views for the Atw NetBox plugin.

Two flows:

1. **Standard CRUD** for :class:`ImportJob` (list / detail / edit / delete) so
   users can audit population history from the NetBox UI.
2. **Two-step import wizard** (:class:`ImportStartView` →
   :class:`ImportConfirmView`) that drives :mod:`netbox_atw.importer` to
   preview (dry-run) and then commit a bulk population from pasted CSV/TSV.
"""

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from netbox.views import generic

from . import filtersets, forms, tables
from .choices import ImportJobStatusChoices
from .import_specs import available_specs, get_import_spec
from .importer import Importer, ImporterError
from .models import ImportJob

# --------------------------------------------------------------------------- #
# Import wizard landing page
# --------------------------------------------------------------------------- #


class ImportHomeView(View):
    """Landing page listing available importers and recent import jobs."""

    template_name = "netbox_atw/import_home.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "specs": available_specs(),
                "recent_jobs": ImportJob.objects.all()[:10],
            },
        )


# --------------------------------------------------------------------------- #
# Standard CRUD for ImportJob
# --------------------------------------------------------------------------- #


class ImportJobListView(generic.ObjectListView):
    queryset = ImportJob.objects.all()
    table = tables.ImportJobTable
    filterset = filtersets.ImportJobFilterSet
    filterset_form = forms.ImportJobFilterForm


class ImportJobView(generic.ObjectView):
    queryset = ImportJob.objects.all()


class ImportJobEditView(generic.ObjectEditView):
    queryset = ImportJob.objects.all()
    form = forms.ImportJobForm


class ImportJobDeleteView(generic.ObjectDeleteView):
    queryset = ImportJob.objects.all()


class ImportJobBulkDeleteView(generic.BulkDeleteView):
    queryset = ImportJob.objects.all()
    table = tables.ImportJobTable


# --------------------------------------------------------------------------- #
# Two-step import wizard
# --------------------------------------------------------------------------- #


class ImportStartView(View):
    """Step 1: choose a target spec and paste CSV/TSV data.

    Renders the start form on GET; on a valid POST it runs a dry-run preview and
    renders the confirm step with the per-row outcome.
    """

    template_name = "netbox_atw/import_start.html"

    def get(self, request):
        return render(request, self.template_name, {"form": forms.ImportStartForm()})

    def post(self, request):
        form = forms.ImportStartForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        spec_name = form.cleaned_data["spec"]
        data = form.cleaned_data["data"]
        delimiter = form.cleaned_data["delimiter"]

        try:
            spec = get_import_spec(spec_name)
            preview = Importer(spec).run_text(data, delimiter=delimiter, dry_run=True)
        except ImporterError as exc:
            form.add_error(None, str(exc))
            return render(request, self.template_name, {"form": form})

        # Persist the dry-run ImportJob so the preview is auditable before commit.
        preview_job = ImportJob.objects.create(
            spec=spec_name,
            status=ImportJobStatusChoices.STATUS_COMPLETED,
            dry_run=True,
            delimiter=delimiter,
            data=data,
            summary=preview.summary(),
            created_count=preview.created,
            updated_count=preview.updated,
            skipped_count=preview.skipped,
            errored_count=preview.errored,
            result={"rows": [r.__dict__ for r in preview.rows]},
        )

        confirm_form = forms.ImportConfirmForm(
            initial={
                "spec": spec_name,
                "data": data,
                "delimiter": delimiter,
                "dry_run": True,
            }
        )
        return render(
            request,
            "netbox_atw/import_confirm.html",
            {
                "form": confirm_form,
                "preview": preview,
                "preview_job": preview_job,
                "spec": spec,
            },
        )


class ImportConfirmView(View):
    """Step 2: commit (or re-preview) after the user confirms the dry-run."""

    template_name = "netbox_atw/import_confirm.html"

    def get(self, request):
        # Confirm must be reached via POST from the start view; bounce back.
        return redirect(reverse("plugins:netbox_atw:import_start"))

    def post(self, request):
        form = forms.ImportConfirmForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        spec_name = form.cleaned_data["spec"]
        data = form.cleaned_data["data"]
        delimiter = form.cleaned_data["delimiter"]
        dry_run = form.cleaned_data["dry_run"]

        try:
            spec = get_import_spec(spec_name)
            result = Importer(spec).run_text(data, delimiter=delimiter, dry_run=dry_run)
        except ImporterError as exc:
            form.add_error(None, str(exc))
            return render(request, self.template_name, {"form": form})

        job = ImportJob.objects.create(
            spec=spec_name,
            status=ImportJobStatusChoices.STATUS_COMPLETED,
            dry_run=dry_run,
            delimiter=delimiter,
            data=data,
            summary=result.summary(),
            created_count=result.created,
            updated_count=result.updated,
            skipped_count=result.skipped,
            errored_count=result.errored,
            result={"rows": [r.__dict__ for r in result.rows]},
        )
        return redirect(reverse("plugins:netbox_atw:importjob", kwargs={"pk": job.pk}))
