# Research Brief — CAP-R0-02 Authentication

**Document ID:** RES-R0-02  
**Status:** Complete for Gate A  
**Date:** 2026-07-19

---

## Research question

What authentication approach fits a Django + DRF modular monolith for an internal/professional engineering platform in Release 0, without SSO yet?

## Applicable standards / guidance

| Topic | Reference | Access |
|-------|-----------|--------|
| Password storage | Django password hashers (PBKDF2/Argon2) | Public docs |
| API auth patterns | DRF authentication classes | Public docs |
| OWASP | ASVS auth controls (high-level) | Public |
| Session security | Django session/CSRF guidance | Public |

No wind-engineering standards apply.

## Methodology options

| Option | Pros | Cons | Fit for R0 |
|--------|------|------|------------|
| **DRF TokenAuthentication** | Simple, built-in with `rest_framework.authtoken`, easy tests | Single token per user by default; less ideal for many SPA refresh flows | **Recommended default** |
| SimpleJWT (access + refresh) | Better for SPA later | More moving parts; UD-002 frontend still deferred | Optional later |
| Session auth only for API | Simple with cookies | Awkward for non-browser API clients / future mobile | Admin only |
| OAuth2/OIDC provider | Enterprise SSO-ready | Too large for this increment | Future |

## Recommended methodology

1. Django `contrib.auth` users + admin session login  
2. DRF **TokenAuthentication** for API  
3. Endpoints: login (obtain token), logout (delete token), me  
4. **No public self-registration** in R0 baseline (staff creates users)  
5. Keep default User model for now **if** no custom fields required yet; Gate B may choose early custom user with UUID to avoid painful migrations later  

## Assumptions

- First clients are API tools / future SPA, not end-customer public signup
- English messages only (UD-005)

## Limitations

- Token auth is not as flexible as OAuth2 for third-party apps
- Without rate limiting, login endpoint is brute-force exposed (mitigate later or add simple throttle in Gate B)

## Validation examples

- Login with valid user → 200 + token key  
- Login with bad password → 401  
- `me` without token → 401  
- `me` with token → 200 + username  
- Health without token → 200  

## References

- Django authentication docs (djangoproject.com)  
- Django REST Framework — Authentication  
- OWASP ASVS (authentication chapter, summary level)

## Unresolved decisions for product/architect

- Token vs JWT (recommend Token for CAP-R0-02)  
- Custom user model now vs later  
- Login throttle strength in this increment  

## Recommendation

Approve Gate A scope; at Gate B lock **UD-003 = DRF Token + Django session admin**, decide custom user yes/no, then implement one small PR.
