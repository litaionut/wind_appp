# CAP-R0-02 — Authentication Baseline

**Capability ID:** CAP-R0-02  
**Status:** Accepted (UD-008)  
**Class:** Foundation  
**Language:** English (UD-005)  
**Depends on:** CAP-R0-01 (Accepted)

---

## 1. Problem statement

The platform has no authenticated identity. Without login and API credentials, organizations, projects, and engineering data cannot be protected.

## 2. User role / story

As a **platform user**, I need to authenticate to the API so that later capabilities can authorize my actions per organization and project.

As a **platform administrator**, I need to create user accounts (no public self-signup in this increment) and use Django admin with session login.

## 3. Engineering objective

Establish a minimal, tested authentication baseline: Django users, admin session login, API token login, and a `whoami` endpoint. Keep `/api/v1/health/` public.

## 4. Scope

- Use Django built-in `User` model (no custom user model migration in this increment unless Gate B requires it for future-proofing — see decision)
- Django admin usable with username/password (session auth)
- API login endpoint that issues an auth token (DRF TokenAuthentication proposed)
- API logout / token revoke (as applicable to chosen mechanism)
- `GET /api/v1/auth/me/` (authenticated) returning current user id, username, email
- Password hashing via Django defaults
- English API error messages
- Automated tests: login success/failure, me requires auth, health remains public
- Documentation: how to create a user and obtain a token

## 5. Non-scope

- Organizations, projects, RBAC matrix (later CAP-R0-03+)
- OAuth / SSO / SAML / social login
- JWT refresh-token family (unless Gate B selects JWT — default proposal is DRF Token)
- Public self-registration / email verification
- Password reset email flow
- MFA / passkeys
- Frontend login UI (UD-002 still deferred)
- Rate limiting infrastructure beyond simple notes (may land in later security increment)
- Audit events for login (audit framework is a later capability; may log minimally if cheap)

## 6. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Staff/admin can create users (management command and/or Django admin) |
| FR-02 | Client can obtain an API token with valid username/password |
| FR-03 | Invalid credentials return 401 with English message |
| FR-04 | Authenticated client can call `GET /api/v1/auth/me/` |
| FR-05 | Unauthenticated `me` returns 401 |
| FR-06 | Health endpoint remains publicly accessible |
| FR-07 | Django admin login works with session authentication |

## 7. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Secrets (SECRET_KEY, passwords) never committed |
| NFR-02 | Passwords stored only as hashes |
| NFR-03 | All user-facing auth messages in English |
| NFR-04 | Tests cover positive and negative auth paths |

## 8. Inputs / outputs

| Direction | Content |
|-----------|---------|
| In | username, password |
| Out | auth token; user profile fields on `me` |

## 9. Edge cases

- Inactive user cannot authenticate
- Wrong password does not reveal whether username exists (generic English error)
- Token reuse after logout/revoke fails (per chosen mechanism)

## 10. Dependencies

- CAP-R0-01 accepted
- Resolve UD-003 (auth mechanism) at this Gate A / Gate B sequence
- Organizations (CAP-R0-03) depends on this capability

## 11. Acceptance criteria

- [ ] User creatable via admin or documented management command
- [ ] API login returns token for valid credentials
- [ ] `me` works only when authenticated
- [ ] Health still public
- [ ] Tests green in CI
- [ ] Docs updated (README auth section)
- [ ] Gate D clean of blocker/major; Gate E approved

## 12. Future extensions (backlog)

- Invite-only registration
- Password reset
- JWT + refresh if API clients require it
- SSO
- Login audit events
- Custom User model with UUID if required before first production users (prefer decide at Gate B)
