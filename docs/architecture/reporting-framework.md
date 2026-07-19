# Reporting Framework

**Document ID:** ARCH-006  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Goals

- Controlled generation of engineering outputs (tables, summaries, later PDF/maps)
- Artifacts linked to calculation runs and input versions
- Permission-aware access identical to project data rules

## R0 scope

- `ReportArtifact` metadata model
- Storage of generated files (e.g., JSON/CSV summary)
- Link to `CalculationRun`
- Minimal generator (e.g., health/system report or empty calc summary stub)

## Later scope

- METEO report, energy summary, bankable templates (R2–R4)
- Map exports and isolines (R1/R5)
- Template versioning aligned with calculation-method versions
