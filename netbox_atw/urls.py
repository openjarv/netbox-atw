from django.urls import path

from netbox_atw import views

app_name = "netbox_atw"

urlpatterns = [
    # Import wizard
    path("import/", views.ImportHomeView.as_view(), name="import_home"),
    path("import/start/", views.ImportStartView.as_view(), name="import_start"),
    path("import/confirm/", views.ImportConfirmView.as_view(), name="import_confirm"),
    # ImportJob audit history (standard NetBox CRUD)
    path("import-jobs/", views.ImportJobListView.as_view(), name="importjob_list"),
    path("import-jobs/add/", views.ImportJobEditView.as_view(), name="importjob_add"),
    path("import-jobs/<int:pk>/", views.ImportJobView.as_view(), name="importjob"),
    path("import-jobs/<int:pk>/edit/", views.ImportJobEditView.as_view(), name="importjob_edit"),
    path("import-jobs/<int:pk>/delete/", views.ImportJobDeleteView.as_view(), name="importjob_delete"),
    path("import-jobs/delete/", views.ImportJobBulkDeleteView.as_view(), name="importjob_bulk_delete"),
]
