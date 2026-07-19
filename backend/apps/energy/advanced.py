"""Advanced energy helpers: MCP, Jensen wake stub, uncertainty."""

from __future__ import annotations

import math
from typing import Any

from apps.energy.models import EnergyAssessment
from apps.energy.services import EnergyError, calculate_gross_energy
from apps.gis.distances import pairwise_distances
from apps.gis.models import TurbinePosition
from apps.gis.spacing import angle_difference_deg, directional_bearing_deg


def mcp_linear(
    *,
    target_means: list[float],
    reference_means: list[float],
) -> dict[str, Any]:
    """Simple concurrent MCP: V_target = a + b * V_ref (least squares)."""
    if len(target_means) != len(reference_means) or len(target_means) < 2:
        raise EnergyError("MCP requires >=2 paired concurrent means")
    n = len(target_means)
    mean_t = sum(target_means) / n
    mean_r = sum(reference_means) / n
    num = sum((r - mean_r) * (t - mean_t) for r, t in zip(reference_means, target_means))
    den = sum((r - mean_r) ** 2 for r in reference_means)
    if den == 0:
        raise EnergyError("Reference variance is zero")
    b = num / den
    a = mean_t - b * mean_r
    predicted = [a + b * r for r in reference_means]
    ss_res = sum((t - p) ** 2 for t, p in zip(target_means, predicted))
    ss_tot = sum((t - mean_t) ** 2 for t in target_means)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot else 0.0
    return {
        "method_version": "mcp_linear_v1",
        "slope_b": b,
        "intercept_a": a,
        "r_squared": r2,
        "samples": n,
        "equation": "V_target = a + b * V_reference",
    }


def jensen_wake_loss_fraction(
    positions: list[TurbinePosition],
    *,
    wind_direction_deg: float,
    thrust_coeff: float = 0.8,
    wake_decay_k: float = 0.04,
    sector_half_width_deg: float = 30.0,
    default_rotor_diameter_m: float = 120.0,
) -> dict[str, Any]:
    """Very simplified single-wake Jensen-inspired loss estimate (engineering stub).

    Not a bankable wake model — versioned as wake_jensen_initial_v1.
    """
    if len(positions) < 2:
        return {
            "method_version": "wake_jensen_initial_v1",
            "wake_loss_fraction": 0.0,
            "pairs_considered": 0,
        }

    by_id = {str(p.id): p for p in positions}
    deficits: list[float] = []
    pairs = 0
    for pair in pairwise_distances(positions):
        a = by_id[pair.from_id]
        b = by_id[pair.to_id]
        bearing = directional_bearing_deg(a.x, a.y, b.x, b.y)
        if angle_difference_deg(bearing, wind_direction_deg) > sector_half_width_deg:
            # try reverse order as upstream
            bearing = directional_bearing_deg(b.x, b.y, a.x, a.y)
            if angle_difference_deg(bearing, wind_direction_deg) > sector_half_width_deg:
                continue
            upstream, _downstream = b, a
        else:
            upstream, _downstream = a, b

        d = (
            upstream.turbine_model.rotor_diameter_m
            if upstream.turbine_model_id
            else default_rotor_diameter_m
        )
        x = max(pair.distance_m, 1.0)
        # Jensen radius growth
        rw = d / 2.0 + wake_decay_k * x
        # velocity deficit at hub (simplified centerline)
        deficit = (1.0 - math.sqrt(max(0.0, 1.0 - thrust_coeff))) * (d / (2.0 * rw)) ** 2
        deficit = max(0.0, min(0.5, deficit))
        deficits.append(deficit)
        pairs += 1

    mean_deficit = sum(deficits) / len(deficits) if deficits else 0.0
    # Convert mean speed deficit to approx energy loss ~ 3 * deficit for small deficits
    wake_loss = max(0.0, min(0.5, 1.0 - (1.0 - mean_deficit) ** 3))
    return {
        "method_version": "wake_jensen_initial_v1",
        "wake_loss_fraction": wake_loss,
        "mean_speed_deficit": mean_deficit,
        "pairs_considered": pairs,
        "wind_direction_deg": wind_direction_deg,
        "assumptions": {
            "thrust_coeff": thrust_coeff,
            "wake_decay_k": wake_decay_k,
            "note": "Initial engineering stub — not for bankable EYA",
        },
    }


def uncertainty_p50_p90(
    assessment: EnergyAssessment,
    *,
    combined_uncertainty: float = 0.12,
) -> dict[str, Any]:
    """P50/P90 from net AEP assuming normal uncertainty on energy.

    P90 ≈ P50 * (1 - 1.28155 * u) for one-sided 90% exceedance.
    """
    if not assessment.results:
        calculate_gross_energy(assessment)
    p50 = float(assessment.results.get("plant_net_aep_mwh") or 0.0)
    u = max(0.0, float(combined_uncertainty))
    p90 = max(0.0, p50 * (1.0 - 1.28155156554 * u))
    return {
        "method_version": "uncertainty_normal_v1",
        "p50_aep_mwh": p50,
        "p90_aep_mwh": p90,
        "combined_uncertainty": u,
        "unit": "MWh",
        "note": "Normal exceedance approximation; category breakdown deferred",
    }
