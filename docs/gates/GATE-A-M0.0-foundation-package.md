# Gate A Report — M0.0 Foundation Package + CAP-R0-01

**Report ID:** GATE-A-2026-07-19-001  
**Presenter:** Coordinator Agent (with Product + Research + Architect inputs)  
**Date:** 2026-07-19  
**Status:** Approved by human product owner (2026-07-19)  

---

## Capability

**M0.0 — Platform governance package** (documentation system of record)  
**CAP-R0-01 — Application skeleton, health-check, CI** (first implementation candidate; approval to proceed to Gate B only)

## Objective

Establish product vision, roadmap, operating model, and the smallest first foundation increment — without writing production application code until approved.

## Current status

**Waiting for approval** (Gate A). Documentation drafted under `/docs`. Repository previously empty; no application code implemented.

## Confirmed decisions

| ID | Outcome |
|----|---------|
| UD-001 | Approved |
| AD-001 | Approved |
| UD-002 | Deferred |
| UD-003 | Deferred |
| UD-004 | Approved (with English-language condition → UD-005) |
| UD-005 | Approved — application language English |

## Assumptions

| ID | Assumption |
|----|------------|
| A-PV-001 | Single-cloud/self-hosted sufficient for early releases |
| A-PV-002 | UI language English for R0 |
| A-RM-001 | Modular Django monolith acceptable through at least R3 |
| A-RM-002 | PostGIS from R1; not required in CAP-R0-01 |
| A-CAP-01 | Docker available on developer machines for Postgres |

## Proposed implementation

### Delivered now (documentation only)

1. Product vision  
2. Complete release roadmap R0–R9 with classifications  
3. Dependency map  
4. Proposed repository structure  
5. Documentation structure  
6. Agent collaboration workflow  
7. Approval-gate process  
8. Versioning and rollback strategy  
9. Calculation-framework concept  
10. Release 0 milestone plan  
11. CAP-R0-01 as first small capability  

### Next (only after approval)

Gate B for CAP-R0-01 → then Gate C implementation of skeleton/health/CI.

## Engineering methodology

Not applicable for M0.0/CAP-R0-01 (no engineering calculation).  
Research note: stack choice references common industry practice for scientific/engineering web platforms (Django + PostgreSQL); no proprietary material used.

## Architecture impact

- Establishes modular monolith direction (AD-001 proposed)
- Defines domain map for R0 entities
- Defines calc framework conceptually (implementation in later R0 caps)
- CAP-R0-01 would add `backend/`, CI, Docker Compose — no domain schema yet

## Security impact

- No auth yet in CAP-R0-01 (explicit non-scope)
- Security architecture documented so R0 does not defer isolation design
- Risk: public health endpoint is intentional and must not leak secrets

## Increment plan

1. **Now:** Approve governance docs + decisions (this Gate A)  
2. **Next:** Gate B detailed design for CAP-R0-01  
3. **Then:** Implement CAP-R0-01 only  
4. **Then:** Auth → Orgs → … per R0 plan  

## Tests and validation

- M0.0: document completeness review against prompt sections 12–16  
- CAP-R0-01 (later): health API test + CI green + smoke run  

## Risks and limitations

| Risk | Mitigation |
|------|------------|
| Roadmap too ambitious → pressure to big-bang | Only M0.1 detailed; R1+ high-level |
| Stack choice regret | ADR process; CAP-R0-01 keeps surface small |
| Empty git history / no remote | Initialize git after approval if desired |
| Frontend/auth undecided | Explicit UD-002/UD-003 deferral |

## Acceptance criteria (Gate A)

- [ ] Product owner accepts vision and R0-first roadmap structure  
- [ ] Product owner accepts agent/gate operating model  
- [ ] Product owner accepts ≤5 kickoff decisions (see below)  
- [ ] No production code started before those approvals  

## Decision required

Exactly **five** human decisions:

| ID | Decision | Options | Coordinator recommendation |
|----|----------|---------|------------------------------|
| **UD-001** | Adopt vision, roadmap R0–R9, docs/agent/gate system of record | Approve / Amend / Reject | **Approve** |
| **AD-001** | Modular Django monolith + DRF + PostgreSQL as default R0 stack | Approve / Alternative stack / Reject | **Approve** |
| **UD-002** | Frontend framework binding | Defer until first UI capability / Choose React now / Choose Vue now / Other | **Defer** |
| **UD-003** | Auth approach binding for R0 | Defer to auth Gate B / Session+Token now / Other | **Defer to auth Gate B** (document direction: Django-standard session + API tokens) |
| **UD-004** | Authorize CAP-R0-01 to proceed to Gate B (skeleton, health, CI) as first implementation | Approve / Amend scope / Reject | **Approve** |

---

**Coordinator recommendation:** Approve UD-001, AD-001, UD-004; defer UD-002 and UD-003 as proposed. Do not start Gate C until Gate B for CAP-R0-01 is approved.
