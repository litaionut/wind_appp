# AD-012 — CAP-R1 layout pack (catalogue → exports)

**Status:** Approved (UD-008)

Implements R1 layout capabilities without PostGIS geometries yet:

- Turbine manufacturer/model catalogue + CSV import
- Turbine positions CRUD + CSV import
- Pairwise distances (planar metres / geodesic for EPSG:4326)
- Directional spacing check (RD multiples)
- Boundaries / exclusion zones as GeoJSON JSONField
- Point-in-polygon spatial validation
- GeoJSON + CSV layout exports
