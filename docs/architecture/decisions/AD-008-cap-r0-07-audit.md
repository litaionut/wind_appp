# AD-008 — CAP-R0-07 Audit Event Framework

**Status:** Approved (UD-008)

## Decision

1. App `apps.audit` with append-only `AuditEvent`.
2. Fields: UUID, action, actor, organization, project, entity_type, entity_id, metadata (JSON), created_at, ip_address.
3. Helper `record_event(...)` used from org/project/identity flows.
4. Read API: org admins/auditors list org events; project members with admin role list project events.
5. No update/delete endpoints.
