# Security Architecture

**Document ID:** ARCH-004 / feeds SD-* decisions  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Threat model (initial)

| Threat | Control (R0 direction) |
|--------|------------------------|
| Cross-org data access (IDOR) | Mandatory org/project scoping in querysets + object-level permission checks |
| Privilege escalation | Least-privilege RBAC; admin actions audited |
| Unauthorized file download | Signed/authorized file access via metadata ACL |
| Secret leakage | Env-based secrets; never commit credentials |
| Malicious uploads | Type/size validation; malware scanning policy TBD |
| Audit tampering | Append-only audit events; restricted delete |
| Brute force / abuse | Rate limiting at API gateway/app layer |

## Permission model (proposed)

### Organization roles (draft)

- `org_admin`
- `org_member`
- `org_auditor` (read + audit)

### Project roles (draft)

- `project_admin`
- `project_engineer`
- `project_viewer`

Exact matrix finalized in CAP for permissions (R0-07), not in skeleton increment.

## Security from Release 0

Security is not deferred:

- Auth before domain data
- Org isolation tests before engineering modules
- Audit framework before high-value files/results
- Secure defaults in settings (DEBUG off in prod, HTTPS, CSRF, secure cookies as applicable)

## Open security decisions

Tracked as SD-* at Gate A / subsequent gates (auth mechanism, retention, malware scanning).
