"""Environmental receptors and simplified impact calculations."""

from __future__ import annotations

import math
import uuid

from django.conf import settings
from django.db import models

from apps.gis.models import TurbinePosition
from apps.projects.models import Project


class Receptor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="receptors")
    name = models.CharField(max_length=255)
    x = models.FloatField()
    y = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]


class ImpactRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="impact_runs")
    name = models.CharField(max_length=255)
    method_version = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


def noise_iso9613_stub(
    turbines: list[TurbinePosition],
    receptors: list[Receptor],
    *,
    source_lw_db: float = 105.0,
) -> dict:
    """Geometric spreading stub (not full ISO 9613). Version noise_spreading_v1."""
    rows = []
    for rec in receptors:
        levels = []
        for t in turbines:
            dist = max(1.0, math.hypot(rec.x - t.x, rec.y - t.y))
            # Lp = Lw - 20*log10(r) - 11
            lp = source_lw_db - 20.0 * math.log10(dist) - 11.0
            levels.append(lp)
        # incoherent sum
        if levels:
            lin = sum(10 ** (lp / 10.0) for lp in levels)
            total = 10.0 * math.log10(lin)
        else:
            total = None
        rows.append({"receptor": rec.name, "level_db": total, "unit": "dB"})
    return {"method_version": "noise_spreading_v1", "receptors": rows}


def shadow_hours_stub(
    turbines: list[TurbinePosition],
    receptors: list[Receptor],
    *,
    max_distance_m: float = 1500.0,
) -> dict:
    """Crude distance-based shadow exposure proxy. Version shadow_distance_v1."""
    rows = []
    for rec in receptors:
        hours = 0.0
        for t in turbines:
            dist = math.hypot(rec.x - t.x, rec.y - t.y)
            rd = t.turbine_model.rotor_diameter_m if t.turbine_model_id else 120.0
            if dist <= max_distance_m:
                # proxy: closer and larger rotor → more theoretical hours
                hours += max(0.0, (1.0 - dist / max_distance_m)) * (rd / 100.0) * 30.0
        rows.append({"receptor": rec.name, "shadow_hours_proxy": hours, "unit": "h/year"})
    return {"method_version": "shadow_distance_v1", "receptors": rows}
