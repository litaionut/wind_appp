# AD-013 — CAP-R2 METEO Foundation

**Status:** Approved (UD-008)

1. App `apps.meteo`.
2. `MeasurementCampaign` under project; structure type mast/lidar/sodar.
3. `Sensor` with height_m, variable (wind_speed, wind_direction, temperature, pressure).
4. `TimeSeriesPoint` (campaign, sensor, timestamp UTC, value, qc_flag).
5. CSV import: `timestamp,sensor_code,value` with timezone assumed UTC.
6. Basic QC: missing detection (gaps), range checks, availability %.
7. Wind rose + mean air density stubs from imported data.
