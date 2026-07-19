"""Pairwise turbine distance calculations."""

from __future__ import annotations

import math
from dataclasses import dataclass

from pyproj import Geod

from apps.gis.models import ProjectCRSRole, TurbinePosition


@dataclass(frozen=True)
class PairDistance:
    from_label: str
    to_label: str
    from_id: str
    to_id: str
    distance_m: float
    method: str


def pairwise_distances(positions: list[TurbinePosition]) -> list[PairDistance]:
    if len(positions) < 2:
        return []

    epsg = _resolve_epsg(positions)
    use_geodesic = epsg == 4326
    geod = Geod(ellps="WGS84") if use_geodesic else None
    results: list[PairDistance] = []

    for i, a in enumerate(positions):
        for b in positions[i + 1 :]:
            if use_geodesic and geod is not None:
                _az12, _az21, dist = geod.inv(a.x, a.y, b.x, b.y)
                method = "geodesic_wgs84"
                distance_m = float(dist)
            else:
                distance_m = math.hypot(a.x - b.x, a.y - b.y)
                method = "planar_metres"
            results.append(
                PairDistance(
                    from_label=a.label,
                    to_label=b.label,
                    from_id=str(a.id),
                    to_id=str(b.id),
                    distance_m=distance_m,
                    method=method,
                )
            )
    return results


def _resolve_epsg(positions: list[TurbinePosition]) -> int | None:
    first = positions[0]
    if first.crs_id:
        return first.crs.epsg_code
    link = first.project.crs_links.filter(role=ProjectCRSRole.HORIZONTAL).select_related(
        "crs"
    ).first()
    if link:
        return link.crs.epsg_code
    return None
