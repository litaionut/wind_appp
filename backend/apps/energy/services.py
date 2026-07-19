"""Power curve interpolation and gross energy calculation."""

from __future__ import annotations

import csv
import io
from typing import Any

from apps.energy.models import CtCurve, CtCurvePoint, EnergyAssessment, PowerCurve, PowerCurvePoint
from apps.gis.models import TurbinePosition


class EnergyError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def import_power_curve_csv(power_curve: PowerCurve, text: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or not {"ws_m_s", "power_kw"}.issubset(
        {h.strip() for h in reader.fieldnames}
    ):
        raise EnergyError("CSV must include ws_m_s,power_kw")
    power_curve.points.all().delete()
    created = 0
    for row in reader:
        PowerCurvePoint.objects.create(
            power_curve=power_curve,
            wind_speed_m_s=float(row["ws_m_s"]),
            power_kw=float(row["power_kw"]),
        )
        created += 1
    if created < 2:
        raise EnergyError("Power curve requires at least 2 points")
    return {"points": created}


def import_ct_curve_csv(ct_curve: CtCurve, text: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or not {"ws_m_s", "ct"}.issubset(
        {h.strip() for h in reader.fieldnames}
    ):
        raise EnergyError("CSV must include ws_m_s,ct")
    ct_curve.points.all().delete()
    created = 0
    for row in reader:
        ct = float(row["ct"])
        if ct < 0 or ct > 1.05:
            raise EnergyError(f"ct out of range at ws={row['ws_m_s']}: {ct}")
        CtCurvePoint.objects.create(
            ct_curve=ct_curve,
            wind_speed_m_s=float(row["ws_m_s"]),
            ct=ct,
        )
        created += 1
    if created < 2:
        raise EnergyError("Ct curve requires at least 2 points")
    return {"points": created}


def interpolate_power_kw(power_curve: PowerCurve, ws: float) -> float:
    points = list(power_curve.points.order_by("wind_speed_m_s"))
    if not points:
        raise EnergyError("Power curve has no points")
    if ws <= points[0].wind_speed_m_s:
        return points[0].power_kw
    if ws >= points[-1].wind_speed_m_s:
        return points[-1].power_kw
    for i in range(1, len(points)):
        a, b = points[i - 1], points[i]
        if a.wind_speed_m_s <= ws <= b.wind_speed_m_s:
            if b.wind_speed_m_s == a.wind_speed_m_s:
                return b.power_kw
            t = (ws - a.wind_speed_m_s) / (b.wind_speed_m_s - a.wind_speed_m_s)
            return a.power_kw + t * (b.power_kw - a.power_kw)
    return 0.0


def calculate_gross_energy(assessment: EnergyAssessment) -> dict[str, Any]:
    distribution = assessment.wind_distribution
    if not isinstance(distribution, list) or not distribution:
        raise EnergyError("wind_distribution must be a non-empty list")

    turbine_count = TurbinePosition.objects.filter(project=assessment.project).count()
    if turbine_count == 0:
        turbine_count = 1

    energy_kwh = 0.0
    hours_total = 0.0
    for bin_row in distribution:
        ws = float(bin_row["ws_m_s"])
        hours = float(bin_row["hours"])
        hours_total += hours
        power_kw = interpolate_power_kw(assessment.power_curve, ws)
        energy_kwh += power_kw * hours

    per_turbine_mwh = energy_kwh / 1000.0
    wake = max(0.0, min(0.95, float(assessment.wake_loss_fraction)))
    net_per_turbine_mwh = per_turbine_mwh * (1.0 - wake)
    plant_gross_mwh = per_turbine_mwh * turbine_count
    plant_net_mwh = net_per_turbine_mwh * turbine_count

    results = {
        "method_version": assessment.method_version,
        "hours_total": hours_total,
        "turbine_count": turbine_count,
        "per_turbine_gross_aep_mwh": per_turbine_mwh,
        "per_turbine_net_aep_mwh": net_per_turbine_mwh,
        "plant_gross_aep_mwh": plant_gross_mwh,
        "plant_net_aep_mwh": plant_net_mwh,
        "wake_loss_fraction": wake,
        "unit": "MWh",
        "air_density_ref_kg_m3": assessment.power_curve.air_density_ref_kg_m3,
    }
    assessment.results = results
    assessment.save(update_fields=["results"])
    return results
