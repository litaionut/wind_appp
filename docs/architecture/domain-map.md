# Domain Map

**Document ID:** ARCH-002  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Core platform entities (Release 0)

| Entity | Description | Isolation |
|--------|-------------|-----------|
| User | Authenticated identity | Global identity; access via memberships |
| Organization | Tenant boundary | Root isolation key |
| OrganizationMembership | User ↔ Org + org role | Org-scoped |
| Project | Engineering workspace | Belongs to one Organization |
| ProjectMembership | User ↔ Project + project role | Project-scoped |
| AuditEvent | Immutable security/engineering trail | Org/project scoped |
| FileObject | Metadata for stored files | Org/project scoped |
| CalculationMethod | Registry entry (id + version) | Global catalogue; usage audited |
| CalculationRun | One execution instance | Org/project scoped |
| CalculationLog | Status/log lines for a run | Via CalculationRun |
| ReportArtifact | Generated output file/metadata | Org/project scoped |

## Later domain clusters (not modelled in R0 detail)

| Cluster | Release | Example entities |
|---------|---------|------------------|
| GIS | R1 | CRS, TurbineModel, TurbinePosition, Boundary, ExclusionZone |
| METEO | R2 | MeasurementCampaign, Sensor, TimeSeries, QCFlag |
| Energy | R3–R4 | PowerCurve, WakeRun, LossTable, UncertaintyCase |
| Environment | R5 | Receptor, NoiseRun, ShadowRun |
| Suitability | R6 | SiteConditionCase, LoadResponseImport |
| Operations | R7 | ScadaChannel, AvailabilityKPI |
| Electrical/Financial | R8 | CableSegment, CapexItem, FinancialCase |
| Hybrid | R9 | PvPlant, GridConstraint, HybridCurtailment |

## Relationship sketch (R0)

```text
Organization 1──* Project
Organization 1──* OrganizationMembership *──1 User
Project 1──* ProjectMembership *──1 User
Project 1──* FileObject
Project 1──* CalculationRun *──1 CalculationMethod
CalculationRun 1──* CalculationLog
CalculationRun 1──* ReportArtifact
* ── AuditEvent (references org/project/actor/entity)
```
