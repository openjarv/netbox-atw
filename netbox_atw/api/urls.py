from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.register("import-jobs", views.ImportJobViewSet)

app_name = "netbox_atw"
urlpatterns = router.urls
