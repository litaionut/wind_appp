# AD-005 — CAP-R0-04 Organization Membership API

**Status:** Approved (UD-008)  
**Date:** 2026-07-19

## Decision

Nested under organization:

- `GET /api/v1/organizations/{org_id}/members/` — members (org members)
- `POST .../members/` — add by username (org_admin); body `{username, role}`
- `PATCH .../members/{membership_id}/` — change role (org_admin)
- `DELETE .../members/{membership_id}/` — remove (org_admin)

Rules:

- Cannot remove the last `org_admin`
- Cannot demote the last `org_admin`
- Target user must already exist (no invite/email flow)
