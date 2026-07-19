"""Release 0 end-to-end foundation flow."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.calculations.models import CalculationMethod, MethodStatus
from apps.files.models import FileObject
from apps.reporting.models import ReportArtifact


@pytest.mark.django_db
def test_r0_end_to_end_foundation_flow() -> None:
    CalculationMethod.objects.get_or_create(
        method_id="platform_stub",
        version="v1",
        defaults={
            "title": "Platform stub calculation",
            "status": MethodStatus.APPROVED_DEFAULT,
        },
    )
    User.objects.create_user(username="e2e", password="pass-e2e-12345")
    client = APIClient()

    login = client.post(
        reverse("auth-login"),
        {"username": "e2e", "password": "pass-e2e-12345"},
        format="json",
    )
    assert login.status_code == status.HTTP_200_OK
    client.credentials(HTTP_AUTHORIZATION=f"Token {login.json()['token']}")

    org = client.post(
        reverse("organization-list"), {"name": "E2E Org"}, format="json"
    )
    assert org.status_code == status.HTTP_201_CREATED
    org_id = org.json()["id"]

    project = client.post(
        reverse("organization-projects", kwargs={"org_id": org_id}),
        {"name": "E2E Project"},
        format="json",
    )
    assert project.status_code == status.HTTP_201_CREATED
    project_id = project.json()["id"]

    upload = client.post(
        reverse("project-files", kwargs={"project_id": project_id}),
        {"file": SimpleUploadedFile("input.txt", b"e2e-data", content_type="text/plain")},
        format="multipart",
    )
    assert upload.status_code == status.HTTP_201_CREATED
    assert FileObject.objects.filter(id=upload.json()["id"]).exists()

    run = client.post(
        reverse("project-calculation-runs", kwargs={"project_id": project_id}),
        {
            "method_id": "platform_stub",
            "method_version": "v1",
            "parameters": {"label": "e2e"},
            "input_data_version": upload.json()["checksum_sha256"],
        },
        format="json",
    )
    assert run.status_code == status.HTTP_201_CREATED
    assert run.json()["status"] == "succeeded"
    assert run.json()["results"]["value"] == 42

    report = client.post(
        reverse("project-reports", kwargs={"project_id": project_id}),
        {"calculation_run_id": run.json()["id"]},
        format="json",
    )
    assert report.status_code == status.HTTP_201_CREATED
    assert ReportArtifact.objects.filter(id=report.json()["id"]).exists()

    health = client.get(reverse("health"))
    assert health.status_code == status.HTTP_200_OK

    audit = client.get(
        reverse("organization-audit-events", kwargs={"org_id": org_id})
    )
    assert audit.status_code == status.HTTP_200_OK
    actions = {item["action"] for item in audit.json()}
    assert "organization.created" in actions
    assert "project.created" in actions
    assert "file.uploaded" in actions
    assert "calculation_run.created" in actions
    assert "report.generated" in actions
