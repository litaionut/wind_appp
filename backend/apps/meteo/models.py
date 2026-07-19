"""METEO measurement campaigns, sensors, and time series."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class StructureType(models.TextChoices):
    MAST = "mast", "Met mast"
    LIDAR = "lidar", "Lidar"
    SODAR = "sodar", "Sodar"


class MeasuredVariable(models.TextChoices):
    WIND_SPEED = "wind_speed", "Wind speed"
    WIND_DIRECTION = "wind_direction", "Wind direction"
    TEMPERATURE = "temperature", "Temperature"
    PRESSURE = "pressure", "Pressure"


class QCFlag(models.TextChoices):
    OK = "ok", "OK"
    MISSING = "missing", "Missing"
    RANGE = "range", "Out of range"
    FROZEN = "frozen", "Frozen"
    EXCLUDED = "excluded", "Excluded"


class MeasurementCampaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="measurement_campaigns"
    )
    name = models.CharField(max_length=255)
    structure_type = models.CharField(max_length=16, choices=StructureType.choices)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    elevation_m = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        MeasurementCampaign, on_delete=models.CASCADE, related_name="sensors"
    )
    code = models.CharField(max_length=64)
    variable = models.CharField(max_length=32, choices=MeasuredVariable.choices)
    height_m = models.FloatField()
    unit = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["height_m", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "code"], name="uniq_campaign_sensor_code"
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} ({self.variable} @ {self.height_m}m)"


class TimeSeriesPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        MeasurementCampaign, on_delete=models.CASCADE, related_name="points"
    )
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="points")
    timestamp = models.DateTimeField()
    value = models.FloatField(null=True, blank=True)
    qc_flag = models.CharField(max_length=16, choices=QCFlag.choices, default=QCFlag.OK)

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["campaign", "timestamp"]),
            models.Index(fields=["sensor", "timestamp"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["sensor", "timestamp"], name="uniq_sensor_timestamp"
            )
        ]
