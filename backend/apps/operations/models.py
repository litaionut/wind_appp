"""Operations KPIs and SCADA summary stubs."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class OperationsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="operations_snapshots"
    )
    name = models.CharField(max_length=255)
    method_version = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


def availability_kpi(
    *,
    period_hours: float,
    downtime_hours: float,
    energy_produced_mwh: float,
    energy_expected_mwh: float,
) -> dict:
    """Basic availability and performance ratio. Version ops_kpi_v1."""
    period = max(period_hours, 1e-9)
    availability = max(0.0, min(1.0, 1.0 - downtime_hours / period))
    if energy_expected_mwh > 0:
        performance_ratio = energy_produced_mwh / energy_expected_mwh
    else:
        performance_ratio = None
    return {
        "method_version": "ops_kpi_v1",
        "period_hours": period_hours,
        "downtime_hours": downtime_hours,
        "availability": availability,
        "energy_produced_mwh": energy_produced_mwh,
        "energy_expected_mwh": energy_expected_mwh,
        "performance_ratio": performance_ratio,
        "note": "SCADA import deferred — manual KPI inputs for R7 stub",
    }
