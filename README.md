# Wind Energy Engineering Platform

Modular engineering platform for wind project development, GIS/layout, meteorological analysis, energy yield, environmental and site-suitability studies, operations, and later electrical/financial and hybrid modelling.

**Application language:** English (UD-005).  
**Current release:** **v0.2.0 — Release 0 foundation complete**.

## Quick start

```powershell
cd Wind_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements\dev.txt
copy .env.example .env
docker compose up -d db
.\.venv\Scripts\python backend\manage.py migrate
.\.venv\Scripts\python backend\manage.py createsuperuser
.\.venv\Scripts\python backend\manage.py runserver
```

Postgres is exposed on host port **5433**.

## Core API (v1)

| Area | Endpoints |
|------|-----------|
| Health | `GET /api/v1/health/` |
| Auth | `/api/v1/auth/login|logout|me/` |
| Organizations | `/api/v1/organizations/`, `.../members/` |
| Projects | `/api/v1/organizations/{id}/projects/`, `/api/v1/projects/{id}/`, `.../members/` |
| Audit | `.../audit-events/` |
| Files | `/api/v1/projects/{id}/files/`, `/api/v1/files/{id}/download/` |
| Calculations | `/api/v1/calculation-methods/`, `.../calculation-runs/` |
| Reports | `/api/v1/projects/{id}/reports/` |

Use header: `Authorization: Token <token>`.

## Tests

```powershell
ruff check backend
pytest
```

## Documentation

[docs/README.md](docs/README.md) · [R0 completion](docs/gates/GATE-E-R0-COMPLETION.md)

## Next

Release 1 — GIS and layout (CRS, turbines, spacing). Operating model: [docs/agents/collaboration-workflow.md](docs/agents/collaboration-workflow.md) (UD-008 standing approval).
