"""Calculation registry and run tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.calculations.models import CalculationMethod, MethodStatus, RunStatus
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    CalculationMethod.objects.get_or_create(
        method_id="platform_stub",
        version="v1",
        defaults={
            "title": "Platform stub calculation",
            "description": "stub",
            "status": MethodStatus.APPROVED_DEFAULT,
        },
    )
    user = User.objects.create_user(username="calc_user", password="pass-calc-1")
    org = Organization.objects.create(name="Calc Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Calc Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ENGINEER
    )
    return user, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_list_methods(setup) -> None:
    user, _project = setup
    client = _auth(user)
    response = client.get(reverse("calculation-methods"))
    assert response.status_code == status.HTTP_200_OK
    keys = {item["registry_key"] for item in response.json()}
    assert "platform_stub_v1" in keys


@pytest.mark.django_db
def test_create_and_execute_stub_run(setup) -> None:
    user, project = setup
    client = _auth(user)
    response = client.post(
        reverse("project-calculation-runs", kwargs={"project_id": project.id}),
        {
            "method_id": "platform_stub",
            "method_version": "v1",
            "parameters": {"label": "demo"},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["status"] == RunStatus.SUCCEEDED
    assert body["results"]["value"] == 42
    assert body["results"]["unit"] == "1"

    logs = client.get(
        reverse("calculation-run-logs", kwargs={"run_id": body["id"]})
    )
    assert logs.status_code == status.HTTP_200_OK
    assert len(logs.json()) >= 1
