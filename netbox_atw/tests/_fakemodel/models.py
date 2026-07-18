"""Minimal models for the importer DB-backed unit tests (no NetBox needed)."""

from django.db import models


class FakeSite(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = "tests_fake"

    def __str__(self):
        return self.name


class FakeDevice(models.Model):
    name = models.CharField(max_length=100, unique=True)
    site = models.ForeignKey(FakeSite, on_delete=models.CASCADE, null=True, blank=True)
    serial = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, default="active")

    class Meta:
        app_label = "tests_fake"

    def __str__(self):
        return self.name
