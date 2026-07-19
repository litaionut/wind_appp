"""CSV import helpers for turbine catalogue and positions."""

from __future__ import annotations

import csv
import io
from typing import Any

from apps.gis.models import (
    ProjectCRS,
    ProjectCRSRole,
    TurbineManufacturer,
    TurbineModel,
    TurbinePosition,
)
from apps.projects.models import Project


class ImportErrorDetail(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def import_catalogue_csv(text: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(text))
    required = {
        "manufacturer",
        "model",
        "hub_height_m",
        "rotor_diameter_m",
        "rated_power_kw",
    }
    if reader.fieldnames is None or not required.issubset(
        {h.strip() for h in reader.fieldnames}
    ):
        raise ImportErrorDetail(
            "CSV must include columns: manufacturer,model,hub_height_m,"
            "rotor_diameter_m,rated_power_kw"
        )
    created = 0
    updated = 0
    for row in reader:
        mfr_name = row["manufacturer"].strip()
        model_name = row["model"].strip()
        if not mfr_name or not model_name:
            continue
        manufacturer, _ = TurbineManufacturer.objects.get_or_create(name=mfr_name)
        _obj, was_created = TurbineModel.objects.update_or_create(
            manufacturer=manufacturer,
            name=model_name,
            defaults={
                "hub_height_m": float(row["hub_height_m"]),
                "rotor_diameter_m": float(row["rotor_diameter_m"]),
                "rated_power_kw": float(row["rated_power_kw"]),
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated}


def import_positions_csv(
    *,
    project: Project,
    text: str,
    user,
) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(text))
    required = {"label", "x", "y"}
    if reader.fieldnames is None or not required.issubset(
        {h.strip() for h in reader.fieldnames}
    ):
        raise ImportErrorDetail("CSV must include columns: label,x,y[,z,model]")

    crs = None
    link = ProjectCRS.objects.filter(
        project=project, role=ProjectCRSRole.HORIZONTAL
    ).select_related("crs").first()
    if link:
        crs = link.crs

    created = 0
    updated = 0
    for row in reader:
        label = row["label"].strip()
        if not label:
            continue
        turbine_model = None
        model_name = (row.get("model") or "").strip()
        if model_name:
            turbine_model = TurbineModel.objects.filter(name=model_name).first()
            if turbine_model is None:
                raise ImportErrorDetail(f"Unknown turbine model: {model_name}")
        z_raw = (row.get("z") or "").strip()
        defaults = {
            "x": float(row["x"]),
            "y": float(row["y"]),
            "z": float(z_raw) if z_raw else None,
            "turbine_model": turbine_model,
            "crs": crs,
            "created_by": user,
        }
        _obj, was_created = TurbinePosition.objects.update_or_create(
            project=project,
            label=label,
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated}
