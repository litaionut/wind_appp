# AD-003 — CAP-R0-02 Authentication Design

**Status:** Approved (UD-008 standing approval)  
**Date:** 2026-07-19  
**Depends on:** UD-003, UD-007, SD-001

## Decision

1. New Django app `apps.identity` for auth API views.
2. Django default `User` model (no custom user in this increment).
3. `rest_framework.authtoken` for API tokens.
4. Endpoints under `/api/v1/auth/`:
   - `POST login/` — username + password → `{ "token": "..." }`
   - `POST logout/` — authenticated; delete token
   - `GET me/` — authenticated; user id, username, email, is_staff
5. Default DRF authentication: `TokenAuthentication` + `SessionAuthentication`.
6. Default permission: `IsAuthenticated` globally; health view stays `AllowAny`.
7. Login view uses `AllowAny` + `AnonRateThrottle` (e.g. 20/min).
8. No public registration endpoints.
9. Users created via Django admin or `createsuperuser`.

## Consequences

- Simple, testable baseline before organizations
- JWT can replace/augment tokens later when SPA exists (UD-002)
