# AD-006 — CAP-R0-05 Projects

**Status:** Approved (UD-008)  
**Date:** 2026-07-19

## Decision

1. App `apps.projects`.
2. `Project`: UUID, organization FK, name, slug (unique per org), created_by, timestamps.
3. On create: creator must be org member; auto `ProjectMembership` as `project_admin`.
4. Also ensure org-level access: only org members can create projects in that org.
5. List/retrieve scoped to project membership (superuser sees all).
6. PATCH by `project_admin` only.
7. API: `/api/v1/organizations/{org_id}/projects/` and `/api/v1/projects/{id}/`.

Roles stored: `project_admin`, `project_engineer`, `project_viewer`.  
Full project membership API → CAP-R0-06.
