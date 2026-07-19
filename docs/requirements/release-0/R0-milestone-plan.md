# Release 0 — Milestone Plan

**Document ID:** R0-MP-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Objective

Create the secure, auditable, versioned foundation required by all later engineering modules.

## Suggested implementation order

1. Application skeleton and development environment — **CAP-R0-01** (first)
2. Authentication
3. Organizations
4. Organization membership
5. Projects
6. Project membership and permissions
7. Audit-event framework
8. File metadata and storage
9. Calculation-run model
10. Calculation status and execution logs
11. Versioned calculation-method registry
12. Reporting artifact model
13. Basic report generation
14. Backups, monitoring and rollback
15. Release 0 end-to-end validation

## Milestones

| ID | Name | Capabilities | Exit |
|----|------|--------------|------|
| M0.0 | Governance docs | Vision, roadmap, workflow | Gate A on this package |
| M0.1 | Skeleton | CAP-R0-01 | Gate E → tag `v0.1.0` |
| M0.2 | Identity & tenants | Auth, orgs, membership | Gate E |
| M0.3 | Projects & authz | Projects, permissions, audit | Gate E |
| M0.4 | Files & calculations | Files, runs, logs, registry | Gate E |
| M0.5 | Reporting & ops | Artifacts, basic reports, ops, E2E | R0 Gate E |

## R0 exit criteria

- Org isolation proven by automated tests
- Calculation runs store method + app + actor metadata
- Cross-org file access denied
- Migrations reversible or explicitly excepted with backup plan
- CI green; rollback dry-run documented
- Product-owner approval recorded

## Detailed tasks beyond M0.1

Intentionally **not** fully specified until CAP-R0-01 is accepted and lessons are known.
