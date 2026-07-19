# Wind Energy Engineering Platform

Modular engineering platform for wind project development, GIS/layout, meteorological analysis, energy yield, environmental and site-suitability studies, operations, and later electrical/financial and hybrid modelling.

**Application language:** English (UD-005).  
**Current:** **`v0.3.0`** API roadmap skeleton + first React SPA (`frontend/`).

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

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 · API: http://127.0.0.1:8000  
Postgres host port **5433**.

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
| GIS | CRS, transform, turbine catalogue/positions, distances, spacing-check, boundaries, GeoJSON/CSV |
| METEO / Energy / Env / Suitability / Ops / Financial / Hybrid | See `docs/releases/changelog.md` |

Use header: `Authorization: Token <token>`.

## Tests

```powershell
ruff check backend
pytest
```

## Documentation

[docs/README.md](docs/README.md) · [frontend/README.md](frontend/README.md)

## Next

Interactive project map (CAP-R1-03) and deeper EYA modules after the thin SPA vertical slice.
