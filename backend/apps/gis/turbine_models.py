"""Turbine catalogue and layout positions."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class TurbineManufacturer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TurbineModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manufacturer = models.ForeignKey(
        TurbineManufacturer, on_delete=models.CASCADE, related_name="models"
    )
    name = models.CharField(max_length=255)
    hub_height_m = models.FloatField()
    rotor_diameter_m = models.FloatField()
    rated_power_kw = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["manufacturer__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["manufacturer", "name"],
                name="uniq_turbine_manufacturer_model_name",
            )
        ]

    def __str__(self) -> str:
        return f"{self.manufacturer.name} {self.name}"


class TurbinePosition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="turbine_positions"
    )
    turbine_model = models.ForeignKey(
        TurbineModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
    )
    label = models.CharField(max_length=64)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField(null=True, blank=True)
    crs = models.ForeignKey(
        "gis.CoordinateReferenceSystem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="turbine_positions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="turbine_positions_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["label"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "label"],
                name="uniq_project_turbine_label",
            )
        ]

    def __str__(self) -> str:
        return f"{self.label} @ {self.project}"
