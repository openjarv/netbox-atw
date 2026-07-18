from django.apps import AppConfig


class TestsFakeConfig(AppConfig):
    name = "netbox_atw.tests._fakemodel"
    label = "tests_fake"
    default_auto_field = "django.db.models.BigAutoField"
