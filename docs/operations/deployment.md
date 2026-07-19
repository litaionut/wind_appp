# Deployment (Release 0)

**Document ID:** OPS-003  
**Status:** Active for R0  
**Last updated:** 2026-07-19

## Local / staging

1. Python 3.12 venv + `pip install -r requirements/dev.txt` (or `base.txt` for runtime-only)
2. `copy .env.example .env`
3. `docker compose up -d db` (host port **5433**)
4. `python backend/manage.py migrate`
5. `python backend/manage.py createsuperuser` (optional)
6. `python backend/manage.py runserver`

## Configuration

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Required in production |
| `DJANGO_DEBUG` | `false` in production |
| `POSTGRES_*` | Database connection |
| `APPLICATION_VERSION` | Recorded on calculation runs |

## Production notes (minimum)

- Serve behind HTTPS reverse proxy
- `DEBUG=False`, strong `SECRET_KEY`
- Persist `media/` volume
- Run migrations before starting new app version
- Prefer process manager (systemd/Docker) — topology TBD
