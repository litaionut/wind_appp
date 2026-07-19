"""METEO import, QC, and summary calculations."""

from __future__ import annotations

import csv
import io
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.meteo.models import (
    MeasuredVariable,
    MeasurementCampaign,
    QCFlag,
    TimeSeriesPoint,
)

RANGE_LIMITS = {
    MeasuredVariable.WIND_SPEED: (0.0, 80.0),
    MeasuredVariable.WIND_DIRECTION: (0.0, 360.0),
    MeasuredVariable.TEMPERATURE: (-80.0, 60.0),
    MeasuredVariable.PRESSURE: (600.0, 1100.0),
}


class MeteoImportError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _parse_ts(raw: str) -> datetime:
    dt = parse_datetime(raw.strip())
    if dt is None:
        raise MeteoImportError(f"Invalid timestamp: {raw}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


@transaction.atomic
def import_timeseries_csv(campaign: MeasurementCampaign, text: str) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(text))
    required = {"timestamp", "sensor_code", "value"}
    if reader.fieldnames is None or not required.issubset(
        {h.strip() for h in reader.fieldnames}
    ):
        raise MeteoImportError("CSV must include timestamp,sensor_code,value")

    sensors = {s.code: s for s in campaign.sensors.all()}
    created = 0
    updated = 0
    for row in reader:
        code = row["sensor_code"].strip()
        sensor = sensors.get(code)
        if sensor is None:
            raise MeteoImportError(f"Unknown sensor_code: {code}")
        ts = _parse_ts(row["timestamp"])
        raw_val = (row.get("value") or "").strip()
        value = None if raw_val == "" else float(raw_val)
        qc = QCFlag.OK
        if value is None:
            qc = QCFlag.MISSING
        else:
            lo, hi = RANGE_LIMITS.get(sensor.variable, (None, None))
            if lo is not None and (value < lo or value > hi):
                qc = QCFlag.RANGE
        _obj, was_created = TimeSeriesPoint.objects.update_or_create(
            sensor=sensor,
            timestamp=ts,
            defaults={"campaign": campaign, "value": value, "qc_flag": qc},
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated}


def availability_stats(campaign: MeasurementCampaign) -> dict[str, Any]:
    points = TimeSeriesPoint.objects.filter(campaign=campaign)
    total = points.count()
    ok = points.filter(qc_flag=QCFlag.OK).count()
    by_flag = Counter(points.values_list("qc_flag", flat=True))
    return {
        "total_points": total,
        "ok_points": ok,
        "availability_ratio": (ok / total) if total else 0.0,
        "flags": dict(by_flag),
    }


def wind_rose(
    campaign: MeasurementCampaign, *, speed_code: str, direction_code: str, sectors: int = 12
) -> dict[str, Any]:
    speed_sensor = campaign.sensors.filter(code=speed_code).first()
    dir_sensor = campaign.sensors.filter(code=direction_code).first()
    if speed_sensor is None or dir_sensor is None:
        raise MeteoImportError("speed_code or direction_code not found on campaign")

    speeds = {
        p.timestamp: p.value
        for p in TimeSeriesPoint.objects.filter(
            sensor=speed_sensor, qc_flag=QCFlag.OK, value__isnull=False
        )
    }
    dirs = {
        p.timestamp: p.value
        for p in TimeSeriesPoint.objects.filter(
            sensor=dir_sensor, qc_flag=QCFlag.OK, value__isnull=False
        )
    }
    sector_width = 360.0 / sectors
    counts = [0] * sectors
    speed_sums = [0.0] * sectors
    paired = 0
    for ts, spd in speeds.items():
        direction = dirs.get(ts)
        if direction is None or spd is None:
            continue
        idx = int(direction % 360.0 // sector_width) % sectors
        counts[idx] += 1
        speed_sums[idx] += spd
        paired += 1
    return {
        "sectors": sectors,
        "paired_samples": paired,
        "bins": [
            {
                "sector_index": i,
                "center_deg": i * sector_width + sector_width / 2.0,
                "frequency": (counts[i] / paired) if paired else 0.0,
                "mean_speed_m_s": (speed_sums[i] / counts[i]) if counts[i] else 0.0,
            }
            for i in range(sectors)
        ],
    }


def mean_air_density(
    campaign: MeasurementCampaign, *, temperature_code: str, pressure_code: str
) -> dict[str, Any]:
    """Mean air density using ρ = p / (R_specific * T) with p in Pa, T in K.

    Assumes temperature sensor in °C and pressure sensor in hPa.
    """
    t_sensor = campaign.sensors.filter(code=temperature_code).first()
    p_sensor = campaign.sensors.filter(code=pressure_code).first()
    if t_sensor is None or p_sensor is None:
        raise MeteoImportError("temperature_code or pressure_code not found")

    temps = {
        p.timestamp: p.value
        for p in TimeSeriesPoint.objects.filter(
            sensor=t_sensor, qc_flag=QCFlag.OK, value__isnull=False
        )
    }
    pressures = {
        p.timestamp: p.value
        for p in TimeSeriesPoint.objects.filter(
            sensor=p_sensor, qc_flag=QCFlag.OK, value__isnull=False
        )
    }
    r_specific = 287.05
    densities = []
    for ts, t_c in temps.items():
        p_hpa = pressures.get(ts)
        if p_hpa is None or t_c is None:
            continue
        t_k = t_c + 273.15
        if t_k <= 0:
            continue
        densities.append((p_hpa * 100.0) / (r_specific * t_k))
    if not densities:
        return {"mean_air_density_kg_m3": None, "samples": 0, "unit": "kg/m^3"}
    return {
        "mean_air_density_kg_m3": sum(densities) / len(densities),
        "samples": len(densities),
        "unit": "kg/m^3",
        "method": "ideal_gas_dry_air_v1",
    }


def detect_frozen(campaign: MeasurementCampaign, *, window: int = 6) -> int:
    """Mark runs of identical values as frozen; returns number of points flagged."""
    flagged = 0
    for sensor in campaign.sensors.all():
        points = list(
            TimeSeriesPoint.objects.filter(sensor=sensor, value__isnull=False).order_by(
                "timestamp"
            )
        )
        run_val = None
        run_len = 0
        run_ids: list = []
        for p in points:
            if p.value == run_val:
                run_len += 1
                run_ids.append(p.id)
            else:
                if run_len >= window and run_val is not None:
                    flagged += TimeSeriesPoint.objects.filter(id__in=run_ids).exclude(
                        qc_flag=QCFlag.MISSING
                    ).update(qc_flag=QCFlag.FROZEN)
                run_val = p.value
                run_len = 1
                run_ids = [p.id]
        if run_len >= window:
            flagged += TimeSeriesPoint.objects.filter(id__in=run_ids).exclude(
                qc_flag=QCFlag.MISSING
            ).update(qc_flag=QCFlag.FROZEN)
    return flagged
