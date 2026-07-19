"""Coordinate transformation via pyproj."""

from __future__ import annotations

from pyproj import Transformer
from pyproj.exceptions import CRSError, ProjError


class TransformError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def transform_xy(
    *,
    x: float,
    y: float,
    source_epsg: int,
    target_epsg: int,
) -> tuple[float, float]:
    try:
        transformer = Transformer.from_crs(
            f"EPSG:{source_epsg}",
            f"EPSG:{target_epsg}",
            always_xy=True,
        )
        out_x, out_y = transformer.transform(x, y)
    except (CRSError, ProjError) as exc:
        raise TransformError(str(exc)) from exc
    return float(out_x), float(out_y)
