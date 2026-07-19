# Dependency Map

**Document ID:** DEP-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Release-level dependencies

```mermaid
flowchart TD
  R0[R0 Foundation]
  R1[R1 GIS and Layout]
  R2[R2 METEO]
  R3[R3 Preliminary Energy]
  R4[R4 Advanced EYA]
  R5[R5 Environment]
  R6[R6 Site Suitability]
  R7[R7 Operations]
  R8[R8 Electrical and Financial]
  R9[R9 Solar and Hybrid]

  R0 --> R1
  R1 --> R2
  R2 --> R3
  R3 --> R4
  R1 --> R5
  R2 --> R6
  R3 --> R6
  R0 --> R7
  R3 --> R7
  R4 --> R8
  R7 --> R8
  R4 --> R9
  R7 --> R9
  R8 --> R9
```

## Hard constraints

| Constraint | Rule |
|------------|------|
| No engineering calc modules before R0 stable | Blocking |
| R1 before layout-dependent energy/environment | Blocking |
| R2 before distribution-based energy | Blocking |
| Research before any calculation implementation | Blocking |
| Internal CFD / advanced flow model | Requires separate scientific approval (R4) |

## Soft parallelism

- R5 research may start after R1 map primitives exist  
- R7 data-contract research may start late R3  
- R8 financial methodology research may proceed in parallel with R7 implementation **only** as research, not code  

## R0 internal dependency chain

```text
CAP-R0-01 Skeleton
  → Auth
    → Organizations → Org membership
      → Projects → Project permissions
        → Audit (can start after Auth in parallel with Projects carefully)
        → Files
        → CalculationRun → Logs → Method registry → Report artifacts
          → Basic report generation
          → Ops (backups/monitoring/rollback) — can parallelize after Skeleton
            → R0 E2E validation
```
