"""Solar / hybrid curtailment stubs."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class HybridCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="hybrid_cases")
    name = models.CharField(max_length=255)
    method_version = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


def pv_yield_stub(
    *,
    capacity_mw: float,
    capacity_factor: float = 0.18,
    hours: float = 8760.0,
) -> dict:
    """Flat CF PV yield. Version pv_yield_v1."""
    cf = max(0.0, min(1.0, capacity_factor))
    energy_mwh = capacity_mw * hours * cf
    return {
        "method_version": "pv_yield_v1",
        "capacity_mw": capacity_mw,
        "capacity_factor": cf,
        "annual_energy_mwh": energy_mwh,
        "note": "Constant CF stub — irradiance time series deferred",
    }


def hybrid_curtailment_stub(
    *,
    wind_mw: list[float],
    solar_mw: list[float],
    grid_limit_mw: float,
) -> dict:
    """Shared grid curtailment by clipping sum to limit. Version hybrid_curtail_v1."""
    if len(wind_mw) != len(solar_mw):
        n = min(len(wind_mw), len(solar_mw))
        wind_mw = wind_mw[:n]
        solar_mw = solar_mw[:n]
    delivered = []
    curtailed = []
    for w, s in zip(wind_mw, solar_mw):
        total = max(0.0, w) + max(0.0, s)
        d = min(total, grid_limit_mw)
        delivered.append(d)
        curtailed.append(max(0.0, total - grid_limit_mw))
    return {
        "method_version": "hybrid_curtail_v1",
        "grid_limit_mw": grid_limit_mw,
        "steps": len(delivered),
        "energy_delivered_mwh": sum(delivered),  # assumes 1h steps
        "energy_curtailed_mwh": sum(curtailed),
        "delivered_mw": delivered,
        "curtailed_mw": curtailed,
        "note": "Assumes 1-hour steps; scheduling deferred",
    }
