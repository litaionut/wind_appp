# AD-010 — CAP-R1-01 CRS Model & Transform Service

**Status:** Approved (UD-008)  
**Date:** 2026-07-19

## Decision

1. App `apps.gis` (Release 1 domain).
2. `CoordinateReferenceSystem`: EPSG code (unique), name, auth_name default EPSG.
3. `ProjectCRS`: project FK + CRS FK + role (`horizontal` | `display`).
4. Transform service via **pyproj** (no PostGIS yet for transforms).
5. API: list/create CRS catalogue entries; set project CRS; `POST /api/v1/gis/transform/` for coordinate pairs.
6. PostGIS deferred to CAP-R1 map/geometry increments.
