"""Simple point-in-polygon checks for turbine positions."""

from __future__ import annotations

from typing import Any


def _point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    """Ray casting; ring is list of [x,y] (GeoJSON order)."""
    inside = False
    n = len(ring)
    if n < 4:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        intersect = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-18) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


def point_in_polygon(x: float, y: float, geometry: dict[str, Any]) -> bool:
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if gtype == "Polygon":
        if not coords:
            return False
        if not _point_in_ring(x, y, coords[0]):
            return False
        for hole in coords[1:]:
            if _point_in_ring(x, y, hole):
                return False
        return True
    if gtype == "MultiPolygon":
        return any(
            point_in_polygon(x, y, {"type": "Polygon", "coordinates": poly})
            for poly in coords
        )
    return False
