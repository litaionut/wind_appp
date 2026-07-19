"""Basic report generation."""

from __future__ import annotations

import json

from django.contrib.auth.models import AbstractBaseUser

from apps.audit.services import record_event
from apps.calculations.models import CalculationRun
from apps.files.models import FileObject
from apps.files.storage import build_storage_key, save_bytes
from apps.projects.models import Project
from apps.reporting.models import ReportArtifact


def generate_basic_report(
    *,
    project: Project,
    user: AbstractBaseUser,
    calculation_run: CalculationRun | None = None,
    request=None,
) -> ReportArtifact:
    summary = {
        "project_id": str(project.id),
        "project_name": project.name,
        "organization_id": str(project.organization_id),
        "report_type": "basic_summary_v1",
    }
    if calculation_run is not None:
        summary["calculation_run"] = {
            "id": str(calculation_run.id),
            "method": calculation_run.method.registry_key,
            "status": calculation_run.status,
            "results": calculation_run.results,
        }

    content = json.dumps(summary, indent=2, sort_keys=True).encode("utf-8")
    filename = f"report_{project.slug}.json"
    storage_key = build_storage_key(project.organization_id, project.id, filename)
    size_bytes, checksum = save_bytes(storage_key, content)
    file_obj = FileObject.objects.create(
        organization=project.organization,
        project=project,
        original_name=filename,
        content_type="application/json",
        size_bytes=size_bytes,
        checksum_sha256=checksum,
        storage_key=storage_key,
        uploaded_by=user,
    )
    artifact = ReportArtifact.objects.create(
        organization=project.organization,
        project=project,
        calculation_run=calculation_run,
        name=filename,
        content_type="application/json",
        file=file_obj,
        summary=summary,
        created_by=user,
    )
    record_event(
        action="report.generated",
        actor=user,
        organization=project.organization,
        project=project,
        entity_type="report_artifact",
        entity_id=artifact.id,
        metadata={"name": artifact.name},
        request=request,
    )
    return artifact
