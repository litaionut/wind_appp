# Wind Energy Engineering Platform

Modular engineering platform for wind project development, GIS/layout, meteorological analysis, energy yield, environmental and site-suitability studies, operations, and later electrical/financial and hybrid modelling.

**Application language:** English (UD-005).

## Current status

**CAP-R0-03 organizations** implemented. Next: membership management API (CAP-R0-04).

Stack: Django + DRF + PostgreSQL + Token auth + multi-tenant organizations.

## Documentation

Start at [docs/README.md](docs/README.md).

## Prerequisites

- Python 3.12
- Docker (for local PostgreSQL)
- Git

## Quick start

```powershell
# 1. Clone and enter the repository
cd Wind_app

# 2. Create virtual environment and install dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements\dev.txt

# 3. Environment file
copy .env.example .env

# 4. Start PostgreSQL (host port 5433 → container 5432; avoids clashes with local Postgres on 5432)
docker compose up -d db

# 5. Apply Django migrations (built-in auth tables; no custom domain models yet)
.\.venv\Scripts\python backend\manage.py migrate
.\.venv\Scripts\python backend\manage.py runserver
```

From another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/
```


Expected JSON:

```json
{"status":"ok","service":"wind-platform-api","api_version":"v1"}
```

## Authentication (CAP-R0-02)

Public self-registration is disabled. Create a user first:

```powershell
.\.venv\Scripts\python backend\manage.py createsuperuser
```

Login (obtain token):

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/auth/login/ `
  -ContentType "application/json" `
  -Body '{"username":"YOUR_USER","password":"YOUR_PASSWORD"}'
```

Call authenticated endpoints with header: `Authorization: Token <token>`.

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/login/` | Public |
| POST | `/api/v1/auth/logout/` | Token |
| GET | `/api/v1/auth/me/` | Token |
| GET | `/api/v1/health/` | Public |
| GET/POST | `/api/v1/organizations/` | Token |
| GET/PATCH | `/api/v1/organizations/{id}/` | Token (member / org_admin) |

Creating an organization makes you `org_admin`. You only see organizations you belong to.

## Tests

From the repository root (with venv activated):

```powershell
ruff check backend
pytest
```

## Project layout

```text
backend/           Django project (config + apps.core)
requirements/      pip-tools lockfiles
docs/              Product and engineering system of record
.github/workflows  CI (ruff + pytest)
docker-compose.yml Local PostgreSQL
```

## Rollback (CAP-R0-01)

1. Stop the local server and `docker compose down` (optionally `-v` to drop the DB volume).
2. Remove or revert the CAP-R0-01 commit(s) / tag.
3. Delete `.venv` if needed and reinstall from the previous revision’s lockfile.

## Operating model

Multi-agent workflow with approval gates — see [docs/agents/collaboration-workflow.md](docs/agents/collaboration-workflow.md).
