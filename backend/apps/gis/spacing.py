"""Directional spacing checks between turbines."""

from __future__ import annotations

import math
from dataclasses import dataclass

from apps.gis.distances import pairwise_distances
from apps.gis.models import TurbinePosition


@dataclass(frozen=True)
class SpacingViolation:
    from_label: str
    to_label: str
    distance_m: float
    required_m: float
    direction_deg: float
    rotor_diameters: float


def directional_bearing_deg(x1: float, y1: float, x2: float, y2: float) -> float:
    """Bearing from point 1 to 2 in degrees (0=N, clockwise), planar."""
    angle = math.degrees(math.atan2(x2 - x1, y2 - y1))
    return (angle + 360.0) % 360.0


def angle_difference_deg(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)


def check_directional_spacing(
    positions: list[TurbinePosition],
    *,
    wind_direction_deg: float,
    sector_half_width_deg: float = 30.0,
    min_downstream_rd: float = 5.0,
    min_crosswind_rd: float = 3.0,
    default_rotor_diameter_m: float = 150.0,
) -> list[SpacingViolation]:
    """Flag pairs closer than required RD multiples along/near the wind axis."""
    if len(positions) < 2:
        return []

    by_id = {str(p.id): p for p in positions}
    violations: list[SpacingViolation] = []
    for pair in pairwise_distances(positions):
        a = by_id[pair.from_id]
        b = by_id[pair.to_id]
        rd_a = (
            a.turbine_model.rotor_diameter_m
            if a.turbine_model_id
            else default_rotor_diameter_m
        )
        rd_b = (
            b.turbine_model.rotor_diameter_m
            if b.turbine_model_id
            else default_rotor_diameter_m
        )
        rd = max(rd_a, rd_b)
        bearing = directional_bearing_deg(a.x, a.y, b.x, b.y)
        aligned = angle_difference_deg(bearing, wind_direction_deg) <= sector_half_width_deg
        aligned_rev = (
            angle_difference_deg(bearing, (wind_direction_deg + 180.0) % 360.0)
            <= sector_half_width_deg
        )
        required_rd = min_downstream_rd if (aligned or aligned_rev) else min_crosswind_rd
        required_m = required_rd * rd
        if pair.distance_m + 1e-9 < required_m:
            violations.append(
                SpacingViolation(
                    from_label=pair.from_label,
                    to_label=pair.to_label,
                    distance_m=pair.distance_m,
                    required_m=required_m,
                    direction_deg=wind_direction_deg,
                    rotor_diameters=pair.distance_m / rd if rd else 0.0,
                )
            )
    return violations
