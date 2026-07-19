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
| UD-006 | User | Accept CAP-R0-01 as complete; `v0.1.0` candidate approved | **Approved** | 2026-07-19 | Gate E |
| UD-007 | User | Approve CAP-R0-02 auth baseline scope; proceed to Gate B | **Approved** | 2026-07-19 | Blanket approval |
| UD-003 | User | API auth = DRF TokenAuthentication; Django admin uses session auth | **Approved** | 2026-07-19 | Was deferred; resolved |
| SD-001 | Security | Public self-registration disabled in CAP-R0-02 | **Approved** | 2026-07-19 | Staff/admin creates users |
| UD-008 | User | Standing approval: Coordinator may accept recommended proposals at Gates A/B/E and proceed without waiting for explicit per-gate replies, unless the owner intervenes or a decision is marked high-risk | **Approved** | 2026-07-19 | Owner: “approve all proposals” |
| AD-003 | Architecture | CAP-R0-02 technical design (identity app, token API, default User model, login throttle) | **Approved** | 2026-07-19 | Under UD-008 |
| AD-004 | Architecture | CAP-R0-03 Organizations + minimal membership on create | **Approved** | 2026-07-19 | Under UD-008 |
| AD-005 | Architecture | CAP-R0-04 membership management API | **Approved** | 2026-07-19 | Under UD-008 |

## Deferred decisions (explicitly not blocking)

| ID | Type | Statement | Status | Next review |
|----|------|-----------|--------|-------------|
| UD-002 | User | Frontend framework (React / Vue / other) | **Deferred** | First UI capability |

## Proposed decisions (awaiting approval)

_None — UD-008 standing approval applies to Coordinator recommendations._

## Assumptions (not decisions)

| ID | Assumption | Notes |
|----|------------|-------|
| A-PV-001 | Single-cloud/self-hosted sufficient for early releases | Still open |
| A-PV-003 | Target users are professional engineers | Still open |
| A-RM-001 | Modular monolith acceptable through at least R3 | Reinforced by AD-001 |
| A-RM-002 | PostGIS from R1 | Still open |
| A-AUTH-01 | Users created by staff | Reinforced by SD-001 |
