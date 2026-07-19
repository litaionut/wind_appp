"""IEC site suitability stubs."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class SuitabilityAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="suitability_assessments"
    )
    name = models.CharField(max_length=255)
    method_version = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


def iec_class_stub(
    *,
    vave_m_s: float,
    vref_m_s: float | None = None,
    i_ref: float = 0.16,
) -> dict:
    """Map Vave/Iref to a coarse IEC class label. Version iec_class_v1."""
    vref = vref_m_s if vref_m_s is not None else 5.0 * vave_m_s
    # Coarse bins based on IEC 61400-1 ed.3 style Vref classes
    if vref >= 50:
        wind_class = "I"
    elif vref >= 42.5:
        wind_class = "II"
    elif vref >= 37.5:
        wind_class = "III"
    else:
        wind_class = "S"

    if i_ref >= 0.16:
        turbulence_category = "A"
    elif i_ref >= 0.14:
        turbulence_category = "B"
    else:
        turbulence_category = "C"

    return {
        "method_version": "iec_class_v1",
        "vave_m_s": vave_m_s,
        "vref_m_s": vref,
        "i_ref": i_ref,
        "iec_wind_class": wind_class,
        "turbulence_category": turbulence_category,
        "label": f"IEC {wind_class}{turbulence_category}",
        "note": "Coarse stub — not a full IEC site assessment",
    }


def terrain_complexity_stub(*, elevation_std_m: float, slope_deg: float) -> dict:
    """Simple terrain complexity score. Version terrain_complexity_v1."""
    score = min(1.0, (elevation_std_m / 50.0) * 0.5 + (abs(slope_deg) / 15.0) * 0.5)
    if score < 0.25:
        label = "simple"
    elif score < 0.55:
        label = "moderate"
    else:
        label = "complex"
    return {
        "method_version": "terrain_complexity_v1",
        "elevation_std_m": elevation_std_m,
        "slope_deg": slope_deg,
        "complexity_score": score,
        "complexity_label": label,
    }
