# Product Backlog

**Document ID:** BL-001  
**Status:** Living document  
**Last updated:** 2026-07-19

---

## How to use

- Only **current + next milestone** hold detailed implementation tasks.
- New ideas discovered during implementation go here — they are **not** silently added to the active increment.
- Status values follow the capability workflow (section 6 of the operating prompt).

## Priority bands

| Band | Meaning |
|------|---------|
| P0 | Blocks platform or current release exit |
| P1 | Required for current/next milestone |
| P2 | Recommended |
| P3 | Optional / future |

---

## Completed milestone: M0.0 — Foundation documentation

| ID | Item | Band | Status | Notes |
|----|------|------|--------|-------|
| CAP-DOC-* | Vision, roadmap, workflow, gates, R0 plan | P0 | Accepted | UD-001 |
| CAP-R0-01 | App skeleton + health + CI | P0 | Architecture proposal (Gate B) | UD-004 / UD-005 |

## Completed milestone: M0.1 — Application skeleton

| ID | Item | Band | Status | Notes |
|----|------|------|--------|-------|
| CAP-R0-01 | Application skeleton, health-check, CI | P0 | Accepted | UD-006; tag `v0.1.0` when git ready |

## Active milestone: M0.2 — Identity & tenants

| ID | Item | Band | Status | Dependencies |
|----|------|------|--------|--------------|
| CAP-R0-02 | Authentication baseline | P0 | Accepted | UD-003, SD-001, AD-003 |
| CAP-R0-03 | Organizations | P0 | Accepted | AD-004; creator → org_admin |
| CAP-R0-04 | Organization membership management API | P0 | Next | CAP-R0-03 |

## Parking lot (discovered later — do not implement now)

| ID | Idea | Source | Band |
|----|------|--------|------|
| — | _(empty)_ | — | — |

## Icebox (future releases)

See `roadmap.md` Releases 1–9. No detailed tasks until dependencies and lessons from earlier releases are known.
