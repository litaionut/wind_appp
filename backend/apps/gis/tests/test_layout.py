"""Spacing, boundaries, spatial validation, GeoJSON tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.gis.models import TurbinePosition
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="layout_user", password="pass-layout-1")
    org = Organization.objects.create(name="Layout Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Layout Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    TurbinePosition.objects.create(project=project, label="T1", x=0.0, y=0.0)
    TurbinePosition.objects.create(project=project, label="T2", x=100.0, y=0.0)
    return user, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_spacing_check_finds_violation(setup) -> None:
    user, project = setup
    client = _auth(user)
    response = client.post(
        reverse("project-turbine-spacing", kwargs={"project_id": project.id}),
        {
            "wind_direction_deg": 90.0,
            "min_downstream_rd": 5.0,
            "default_rotor_diameter_m": 150.0,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    # 100 m < 5*150=750 m along E-W wind
    assert response.json()["violation_count"] >= 1


@pytest.mark.django_db
def test_boundary_and_spatial_validation(setup) -> None:
    user, project = setup
    client = _auth(user)
    polygon = {
        "type": "Polygon",
        "coordinates": [[[-10, -10], [50, -10], [50, 50], [-10, 50], [-10, -10]]],
    }
    created = client.post(
        reverse("project-boundaries", kwargs={"project_id": project.id}),
        {
            "name": "Site",
            "kind": "project_boundary",
            "geometry": polygon,
        },
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED

    validation = client.get(
        reverse("project-spatial-validation", kwargs={"project_id": project.id})
    )
    assert validation.status_code == status.HTTP_200_OK
    # T2 at x=100 is outside boundary max x=50
    codes = {i["code"] for i in validation.json()["issues"]}
    assert "outside_boundary" in codes


@pytest.mark.django_db
def test_layout_geojson_export(setup) -> None:
    user, project = setup
    client = _auth(user)
    response = client.get(
        reverse("project-layout-geojson", kwargs={"project_id": project.id})
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["type"] == "FeatureCollection"
    assert len(response.json()["features"]) == 2


@pytest.mark.django_db
def test_turbines_csv_export(setup) -> None:
    user, project = setup
    client = _auth(user)
    response = client.get(
        reverse("project-turbines-csv", kwargs={"project_id": project.id})
    )
    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response["Content-Type"]
    assert "T1" in response.content.decode()

