# AD-011 — CAP-R1-04…06 Turbine Catalogue, Positions, Distances

**Status:** Approved (UD-008)

1. Models in `apps.gis`: `TurbineManufacturer`, `TurbineModel`, `TurbinePosition`.
2. Catalogue CSV import: `manufacturer,model,hub_height_m,rotor_diameter_m,rated_power_kw`.
3. Positions: project-scoped `x,y` (+ optional `z`, label), optional model FK; CSV `label,x,y,z,model`.
4. Coordinates interpreted in project horizontal CRS when set; otherwise stored as-is.
5. Pairwise distances: geodesic (WGS84) if CRS is 4326; else planar metres `hypot(dx,dy)`.
6. APIs under `/api/v1/gis/...` and `/api/v1/projects/{id}/turbines/`.
