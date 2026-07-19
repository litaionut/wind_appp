# Decisions Log

**Document ID:** DL-001  
**Status:** Living  
**Last updated:** 2026-07-19

---

## Confirmed decisions

| ID | Type | Statement | Status | Date | Notes |
|----|------|-----------|--------|------|-------|
| UD-001 | User | Adopt product vision, roadmap R0–R9, docs/agent/gate system of record | **Approved** | 2026-07-19 | Gate A |
| AD-001 | Architecture | Modular Django monolith + DRF + PostgreSQL as default R0 stack | **Approved** | 2026-07-19 | Gate A; see ADR |
| UD-004 | User | CAP-R0-01 (skeleton, health-check, CI) is first implementation; proceed to Gate B | **Approved** | 2026-07-19 | Condition: application language English → UD-005 |
| UD-005 | User | Application language is **English** (UI strings, API messages, user-facing docs in app). i18n deferred. | **Approved** | 2026-07-19 | Stated with UD-004 approval |
| AD-002 | Architecture | CAP-R0-01 technical design (layout, health contract, CI, pip-tools, Python 3.12) | **Approved** | 2026-07-19 | Gate B; proceed to Gate C |
| UD-006 | User | Accept CAP-R0-01 as complete; `v0.1.0` candidate approved | **Approved** | 2026-07-19 | Gate E; tag when git history exists |

## Deferred decisions (explicitly not blocking)

| ID | Type | Statement | Status | Next review |
|----|------|-----------|--------|-------------|
| UD-002 | User | Frontend framework (React / Vue / other) | **Deferred** | Gate B of first UI capability |
| UD-003 | User | Auth mechanism details for R0 | **Deferred** | Gate B of authentication capability |

## Proposed decisions (awaiting approval)

_None._

## Assumptions (not decisions)

| ID | Assumption | Notes |
|----|------------|-------|
| A-PV-001 | Single-cloud/self-hosted sufficient for early releases | Still open |
| A-PV-003 | Target users are professional engineers | Still open |
| A-RM-001 | Modular monolith acceptable through at least R3 | Reinforced by AD-001 |
| A-RM-002 | PostGIS from R1; not in CAP-R0-01 | Still open |
| A-CAP-01 | Docker available on developer machines for Postgres | Used in Gate B design |
