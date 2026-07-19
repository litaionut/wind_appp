"""Power curves and energy assessment cases."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.gis.models import TurbineModel
from apps.projects.models import Project


class PowerCurve(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    turbine_model = models.ForeignKey(
        TurbineModel, on_delete=models.CASCADE, related_name="power_curves"
    )
    name = models.CharField(max_length=255)
    air_density_ref_kg_m3 = models.FloatField(default=1.225)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.turbine_model})"


class PowerCurvePoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    power_curve = models.ForeignKey(
        PowerCurve, on_delete=models.CASCADE, related_name="points"
    )
    wind_speed_m_s = models.FloatField()
    power_kw = models.FloatField()

    class Meta:
        ordering = ["wind_speed_m_s"]
        constraints = [
            models.UniqueConstraint(
                fields=["power_curve", "wind_speed_m_s"],
                name="uniq_power_curve_wind_speed",
            )
        ]


class EnergyAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="energy_assessments"
    )
    name = models.CharField(max_length=255)
    power_curve = models.ForeignKey(PowerCurve, on_delete=models.PROTECT)
    # discrete distribution: [{"ws_m_s": 1, "hours": 100}, ...]
    wind_distribution = models.JSONField(default=list)
    wake_loss_fraction = models.FloatField(default=0.0)
    method_version = models.CharField(max_length=64, default="gross_energy_v1")
    results = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
