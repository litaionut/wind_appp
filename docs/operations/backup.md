# Backup (Release 0)

**Document ID:** OPS-005  
**Status:** Active for R0

## PostgreSQL

Before migrations or releases:

```powershell
docker compose exec db pg_dump -U wind wind_platform > backup_wind_$(Get-Date -Format yyyyMMdd_HHmmss).sql
```

Restore:

```powershell
Get-Content backup_....sql | docker compose exec -T db psql -U wind wind_platform
```

## Object / file storage

Back up the `media/` directory alongside the database. FileObject rows reference `storage_key` paths under `MEDIA_ROOT`.

## Cadence (recommended)

- Daily DB dump for staging/production
- Retain at least 7 daily + 4 weekly dumps
- Test restore quarterly
