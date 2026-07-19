# Release Roadmap

**Document ID:** RM-001  
**Status:** Approved structure (UD-001); R0 active  
**Version:** 0.1.0  
**Last updated:** 2026-07-19

---

## Classification legend

| Class | Meaning |
|-------|---------|
| **Foundation** | Required platform infrastructure; blocks later work |
| **Required** | Must ship for the release to exit |
| **Recommended** | Strongly improves release value; can slip with approval |
| **Optional** | Nice-to-have within release window |
| **Future** | Explicitly deferred; backlog only |

## Scope status legend

- **Approved scope** — product owner has approved for planning/implementation
- **Proposed scope** — documented here; not yet approved for active work
- **Assumptions** — influence planning; not confirmed
- **Unresolved** — must be decided before related implementation

---

## Release overview

| Release | Name | Primary objective | Status |
|---------|------|-------------------|--------|
| R0 | Engineering platform foundation | Secure, auditable, versioned base | **Approved scope — M0.1 at Gate B** |
| R1 | GIS and layout | Coordinates, turbines, spacing, exports | Proposed (high-level) |
| R2 | METEO | Measurements, QC, roses, shear, density | Proposed (high-level) |
| R3 | Preliminary energy | Power curves, gross energy, initial wake | Proposed (high-level) |
| R4 | Advanced EYA | MCP, wakes, uncertainty, P50/P90 | Proposed (high-level) |
| R5 | Environment | Shadow, noise, receptors, curtailment | Proposed (high-level) |
| R6 | Site suitability | IEC conditions, turbulence, terrain | Proposed (high-level) |
| R7 | Operations | SCADA, availability, performance | Proposed (high-level) |
| R8 | Electrical and financial | Cables, losses, LCOE, NPV/IRR | Proposed (high-level) |
| R9 | Solar and hybrid | PV, shared grid, hybrid curtailment | Proposed (high-level) |

**Active detailed planning:** Release 0 only.  
**Next milestone after R0:** Release 1 planning (not detailed until R0 exit criteria met).

---

## Release 0 — Engineering platform foundation

**Exit criteria:** Secure multi-org foundation with auth, projects, permissions, audit, files, calculation-run tracking, method registry, basic reporting artifacts, CI, backups/rollback docs, and end-to-end validation.

| # | Capability / Epic | Class | Complexity | Eng. risk | Validation difficulty | Specialists | Dependencies |
|---|-------------------|-------|------------|-----------|----------------------|-------------|--------------|
| R0-01 | Application skeleton + dev environment | Foundation | S | Low | Low | Architect, Dev, Test | — |
| R0-02 | CI pipeline + automated tests | Foundation | S | Low | Low | Dev, Test | R0-01 |
| R0-03 | Authentication | Foundation | M | Med | Med | Architect, Dev, Test, Reviewer | R0-01 |
| R0-04 | Organizations | Foundation | M | Med | Med | Product, Architect, Dev, Test | R0-03 |
| R0-05 | Organization membership | Foundation | M | Med | Med | Architect, Dev, Test | R0-04 |
| R0-06 | Projects | Foundation | M | Med | Med | Product, Architect, Dev, Test | R0-04 |
| R0-07 | Project membership & permissions | Foundation | L | High | High | Architect, Dev, Test, Reviewer | R0-05, R0-06 |
| R0-08 | Audit-event framework | Foundation | M | Med | Med | Architect, Dev, Test, Reviewer | R0-03 |
| R0-09 | File metadata & storage | Foundation | M | Med | Med | Architect, Dev, Test | R0-06, R0-07 |
| R0-10 | Calculation-run model | Foundation | M | Med | High | Architect, Research, Dev, Test | R0-06 |
| R0-11 | Calculation status & execution logs | Foundation | M | Med | Med | Architect, Dev, Test | R0-10 |
| R0-12 | Versioned calculation-method registry | Foundation | M | High | High | Research, Architect, Dev, Test | R0-10 |
| R0-13 | Reporting artifact model | Foundation | S | Low | Med | Architect, Dev, Test | R0-10 |
| R0-14 | Basic report generation | Recommended | M | Med | Med | Dev, Test, Docs | R0-13 |
| R0-15 | Backups, monitoring, rollback | Foundation | M | Med | Med | Architect, Ops docs, Test | R0-01 |
| R0-16 | Release 0 E2E validation | Required | M | Med | High | Test, Reviewer, Docs | All above |

### R0 acceptance (release level)

- [ ] Org isolation proven by automated permission tests
- [ ] Calculation runs store method version + app version + actor
- [ ] Files inaccessible across organizations
- [ ] Migrations reversible (documented exceptions only)
- [ ] CI green on main-protection path
- [ ] Rollback procedure documented and dry-run tested in staging
- [ ] Product-owner Gate E approval for R0

---

## Release 1 — GIS and layout (high-level)

**Objective:** Project map, turbine catalogue/positions, spacing, boundaries, exclusion zones, basic exports.

| Epic | Class | Complexity | Eng. risk | Validation | Depends on |
|------|-------|------------|-----------|------------|------------|
| CRS & coordinate model | Foundation | M | Med | Med | R0 |
| Coordinate transform service | Required | M | Med | High | CRS |
| Project map | Required | M | Low | Med | CRS |
| Turbine manufacturer/model | Required | S | Low | Low | R0 projects |
| Turbine catalogue import | Required | M | Med | Med | Turbine model |
| Turbine position import | Required | M | Med | Med | CRS, catalogue |
| Layout display / edit | Required | L | Med | Med | Positions, map |
| Pairwise distance | Required | S | Low | High | Positions |
| Directional spacing | Required | M | Med | High | Distances, Research |
| Boundaries & exclusions | Required | M | Med | Med | CRS, PostGIS |
| Spatial validation | Required | M | Med | High | Boundaries |
| GeoJSON / CSV / GIS exports | Recommended | M | Low | Med | Layout |
| R1 validation dataset | Required | M | Med | High | All R1 |

**Detailed tasks:** deferred until R0 accepted.

---

## Release 2 — METEO (high-level)

Measurement campaigns, sensors, time-series import, QC, wind roses, distributions, shear, TI, air density, METEO report.

| Epic | Class | Complexity | Eng. risk | Validation | Depends on |
|------|-------|------------|-----------|------------|------------|
| Campaign / mast / lidar / sodar | Required | M | Med | Med | R0 |
| Sensors & heights | Required | M | Low | Med | Campaign |
| Time-series model | Foundation | L | High | High | R0 files/calc |
| CSV import framework | Required | M | Med | High | Time-series |
| Timestamp/timezone validation | Required | M | High | High | Import |
| QC (missing, range, frozen, exclusions) | Required | L | High | High | Research |
| Availability stats | Required | M | Med | Med | QC |
| Wind sectors / roses / distributions | Required | L | Med | High | Research, QC |
| Shear / TI / air density | Required | L | High | High | Research |
| METEO report | Recommended | M | Med | Med | Reporting R0 |
| R2 benchmarks | Required | L | High | High | All R2 |

---

## Release 3 — Preliminary energy (high-level)

Power curves, simple wind distribution, gross energy, initial wake, per-turbine AEP, basic losses, energy summary.

| Epic | Class | Complexity | Eng. risk | Validation | Depends on |
|------|-------|------------|-----------|------------|------------|
| Power-curve model & import | Required | M | Med | High | R0, R1 turbines |
| Simple wind distribution | Required | M | Med | High | R2 |
| Gross energy | Required | M | Med | High | Power curve + dist |
| Initial wake (researched) | Required | L | High | High | Research, R1 layout |
| Per-turbine / plant AEP | Required | M | High | High | Wake |
| Basic loss table | Required | M | Med | Med | AEP |
| Energy summary report | Recommended | M | Med | Med | Reporting |
| R3 benchmarks | Required | L | High | High | All R3 |

---

## Releases 4–9 (summary)

| Release | Focus | Key risks | Notes |
|---------|-------|-----------|-------|
| R4 Advanced EYA | MCP, flow integrations, multi-wake, TS AEP, uncertainty, P50/P90 | Very high scientific & validation cost | External flow models isolated; no internal CFD without approval |
| R5 Environment | Shadow, noise, receptors, isolines, curtailment | Regulatory variation by country | Versioned regulation parameters |
| R6 Site suitability | IEC site conditions, effective TI, terrain, load-response | Standard-edition precision | Manufacturer data as controlled project data |
| R7 Operations | SCADA contract, availability, expected vs actual | Time-series scale | Raw / cleaned / KPI separation |
| R8 Electrical & financial | Cables, electrical losses, CAPEX/OPEX, LCOE, NPV/IRR | Financial assumption sensitivity | Currency, price basis, formula version required |
| R9 Solar & hybrid | PV, shared grid, export constraint, hybrid curtailment | Shared TS & constraint framework | Design for later storage without core redesign |

---

## Dependency map (release level)

```text
R0 Foundation
 └─► R1 GIS/Layout
      ├─► R2 METEO
      │    └─► R3 Preliminary Energy
      │         └─► R4 Advanced EYA
      │              ├─► R5 Environment (partial parallel after R1 map + R0)
      │              └─► R6 Site Suitability (needs R2 + R3 concepts)
      └─► R7 Operations (needs R0 calc framework + R3 power curves)
           └─► R8 Electrical/Financial (needs energy outputs)
                └─► R9 Solar/Hybrid (needs shared TS + grid constraints from R4/R7/R8)
```

**Parallelism note:** R5 can begin research after R1 maps exist; implementation still gated. R7 research may start late R3. No engineering calculation modules before R0 stable.

---

## Milestones (near term)

| Milestone | Contents | Gate |
|-----------|----------|------|
| M0.0 | Vision, roadmap, docs structure, workflow, R0 plan | Gate A (this package) |
| M0.1 | App skeleton, health check, CI, docs skeleton | Gates B→E for CAP-R0-01 |
| M0.2 | Auth + Organizations + membership | Subsequent capabilities |
| M0.3 | Projects + permissions + audit | … |
| M0.4 | Files + calculation runs + method registry | … |
| M0.5 | Reporting artifacts + ops + R0 E2E | R0 Gate E |

Detailed tasks exist only for **M0.0** (done in this package) and **M0.1** (proposed next).

---

## Current approved scope

- Vision + R0–R9 roadmap structure (UD-001)
- Stack: Django + DRF + PostgreSQL (AD-001)
- Application language: English (UD-005)
- CAP-R0-01 authorized to Gate B (UD-004); implementation waits for AD-002

## Proposed future scope

Releases 1–9 as summarized above.

## Assumptions

| ID | Assumption |
|----|------------|
| A-RM-001 | Modular Django monolith is acceptable through at least R3 |
| A-RM-002 | PostGIS required from R1; R0 may prepare without spatial features |
| A-RM-003 | Background workers needed from first long-running calc (likely R2+) |

## Unresolved decisions

See Gate A report (max five).
