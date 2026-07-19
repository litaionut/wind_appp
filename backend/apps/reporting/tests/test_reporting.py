"""Report generation tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.calculations.models import CalculationMethod, MethodStatus
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole
from apps.reporting.models import ReportArtifact


@pytest.fixture
def setup(db):
    CalculationMethod.objects.get_or_create(
        method_id="platform_stub",
        version="v1",
        defaults={
            "title": "stub",
            "status": MethodStatus.APPROVED_DEFAULT,
        },
    )
    user = User.objects.create_user(username="rep_user", password="pass-rep-1")
    org = Organization.objects.create(name="Rep Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Rep Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    return user, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_generate_report_with_run(setup) -> None:
    user, project = setup
    client = _auth(user)
    run = client.post(
        reverse("project-calculation-runs", kwargs={"project_id": project.id}),
        {"method_id": "platform_stub", "method_version": "v1", "parameters": {"label": "r"}},
        format="json",
    ).json()
    response = client.post(
        reverse("project-reports", kwargs={"project_id": project.id}),
        {"calculation_run_id": run["id"]},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert ReportArtifact.objects.filter(id=response.json()["id"]).exists()
    assert response.json()["summary"]["calculation_run"]["results"]["value"] == 42
