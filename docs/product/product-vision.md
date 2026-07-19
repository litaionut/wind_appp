# Product Vision — Wind Energy Engineering Platform

**Document ID:** PV-001  
**Status:** Approved (UD-001)  
**Version:** 0.1.0  
**Owner:** Product Agent / Coordinator Agent  
**Last updated:** 2026-07-19

---

## Vision statement

Build a modular, auditable engineering platform that supports professional wind (and later hybrid) project work — from site development and GIS layout through meteorological analysis, energy-yield assessment, environmental and site-suitability studies, operations, and financial modelling — with **traceable calculations, versioned inputs, reproducible results, and controlled report generation**.

## Product principles

1. **Engineering correctness over feature breadth** — every calculation is researched, versioned, and independently validated.
2. **Small increments** — one capability, one specification, one PR, one validation result.
3. **Traceability** — inputs, assumptions, method versions, and results are always auditable.
4. **Organization isolation** — multi-tenant security from Release 0.
5. **Reproducibility and rollback** — historical runs remain reproducible; every release can be rolled back.
6. **Human control** — no implementation without explicit approval gates.

## Intended users

| Role | Primary needs |
|------|----------------|
| Wind resource analyst | METEO QC, roses, shear, density, MCP |
| Layout / GIS engineer | Turbine layout, spacing, exclusions, exports |
| Energy-yield engineer | AEP, wake, losses, uncertainty, bankable reports |
| Environmental specialist | Shadow, noise, receptors, curtailment |
| Site-suitability engineer | IEC conditions, turbulence, terrain |
| Operations engineer | SCADA KPIs, expected vs actual |
| Project manager / developer | Project status, reports, decisions |
| Organization admin | Membership, roles, audit, retention |

## Platform scope (long-term)

- Wind project development
- GIS and turbine layout design
- Wind measurements and meteorological analysis
- Energy-yield assessment (preliminary → advanced)
- Environmental assessments
- Site-suitability calculations
- Operational wind-farm performance
- Electrical and financial modelling
- Solar and hybrid projects

## Explicit non-goals (near term)

- Full distributed microservices architecture (modular monolith first)
- Proprietary equation copying without legal clearance
- Bankable EYA before Releases 0–3 foundation and validation gates
- Internal CFD / advanced flow model before separate scientific approval
- Uncontrolled “big bang” delivery of entire modules

## Success criteria (platform level)

- Every engineering value carries explicit units.
- Every calculation run records method ID, method version, app version, input version, user, timestamp, results, warnings.
- Organization and project data isolation is enforced at API and storage layers.
- Releases are tagged, tested, documented, and rollback-ready.
- Capability completion requires product, research, architecture, tests, review, docs, and human approval — not “code runs”.

## Confirmed decisions

| ID | Decision |
|----|----------|
| UD-001 | This vision and R0–R9 operating model adopted |
| UD-005 | Application language is English; i18n deferred |

## Assumptions

| ID | Assumption | Impact if wrong |
|----|------------|-----------------|
| A-PV-001 | Initial deployment is self-hosted or single-cloud; multi-cloud not required in R0 | Ops tooling may need redesign |
| A-PV-003 | Target users are professional engineers, not public consumers | UX can prioritize precision over consumer simplicity |

## Unresolved decisions

See `docs/product/decisions-log.md` (UD-002 frontend, UD-003 auth deferred).
