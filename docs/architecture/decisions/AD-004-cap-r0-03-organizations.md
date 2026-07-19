# AD-004 — CAP-R0-03 Organizations

**Status:** Approved (UD-008)  
**Date:** 2026-07-19

## Decision

1. App `apps.organizations`.
2. `Organization`: UUID PK, name, unique slug, created_by, timestamps.
3. `OrganizationMembership` created in this increment (minimal): on org create, creator becomes `org_admin`. List/retrieve scoped to membership.
4. Roles: `org_admin`, `org_member`, `org_auditor` (enum stored now; CAP-R0-04 manages members).
5. API under `/api/v1/organizations/` — list, create, retrieve, partial update.
6. Update restricted to `org_admin` (and Django superuser).
7. No public org directory; no delete in this increment.

## Out of scope (CAP-R0-04+)

- Invite/add/remove members, role changes via API
- Projects
