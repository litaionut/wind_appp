# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Layout UI: map, add/edit/import turbines, catalogue create + power/Ct CSV (AD-016 / RD-001)
- Ct curves API (`/energy/ct-curves/`) and turbine model POST create
- Position import supports optional `manufacturer` + `model`

### Added (included in `v0.3.0`)

- CAP-R4 advanced EYA stubs: MCP linear, Jensen wake, P50/P90 uncertainty
- CAP-R5 environment: receptors, noise spreading stub, shadow hours proxy
- CAP-R6 site suitability stubs: IEC class, terrain complexity
- CAP-R7 operations stub: availability / performance KPI
- CAP-R8 financial stubs: electrical losses, LCOE/NPV/IRR
- CAP-R9 hybrid stubs: PV yield CF, shared-grid curtailment
- CAP-R3 preliminary energy: power curves + gross_energy_v1 AEP
- CAP-R2 METEO foundation: campaigns, sensors, timeseries import, QC, wind rose, air density
- CAP-R1 layout pack: turbine catalogue/positions, distances, spacing, boundaries, GeoJSON/CSV exports
- CAP-R1-01/02 CRS catalogue, project CRS, pyproj transform API

## [0.3.0] — 2026-07-19

### Added

- API roadmap skeleton tagged: R1–R9 engineering stubs on `main`

## [0.2.0] — 2026-07-19 (Release 0 complete)

### Added

- CAP-R0-08 file metadata + local storage upload/download
- CAP-R0-09…11 calculation method registry, runs, logs, stub executor `platform_stub_v1`
- CAP-R0-12…13 report artifacts + basic JSON report generation
- CAP-R0-14…15 ops docs (deploy/backup/monitor/rollback)
- CAP-R0-16 R0 end-to-end foundation test
- CAP-R0-02…07 auth, orgs, projects, audit (prior commits in 0.2 train)

## [0.1.0] — 2026-07-19

### Added

- Django + DRF application skeleton
- `GET /api/v1/health/`
- Governance documentation under `/docs`
