# Data Architecture

**Document ID:** ARCH-003  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Principles

1. PostgreSQL is the system of record for structured domain data.
2. Object storage holds binary artifacts; DB stores metadata and hashes.
3. Every tenant-owned row includes `organization_id` (and `project_id` when project-scoped).
4. Soft-delete vs hard-delete policies are explicit (see SD decisions).
5. Migrations are reversible where technically possible; destructive steps require backup + ADR.

## Storage tiers

| Tier | Technology | Contents |
|------|------------|----------|
| Relational | PostgreSQL | Entities, permissions, audit, calc metadata |
| Spatial | PostGIS (R1+) | Geometries, spatial indexes |
| Object | S3-compatible | Uploads, reports, large imports |
| Cache/queue | Redis (when workers introduced) | Task broker, short-lived cache |
| Time-series (later) | TBD at R2/R7 research | METEO/SCADA high-volume data |

## Calculation-run data contract (conceptual)

```text
CalculationRun
  id, organization_id, project_id
  calculation_type
  method_id, method_version
  application_version
  input_data_version / input snapshot refs
  parameters (JSON, schema-validated)
  assumptions (JSON)
  status (queued|running|succeeded|failed|cancelled)
  started_at, completed_at
  created_by
  results (JSON or artifact refs)
  warnings[], errors[]
  validation_status
  feature_flag_context
```

## Input versioning

- Immutable snapshots or content-addressed file hashes for inputs used by a run
- Mutating project data after a run must not alter historical run inputs

## Backup & retention (outline)

See `docs/operations/backup.md` and `docs/operations/rollback.md`.
