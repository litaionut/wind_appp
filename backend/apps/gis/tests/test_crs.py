"""CRS and transform tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="gis_user", password="pass-gis-1")
    org = Organization.objects.create(name="GIS Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="GIS Project", created_by=user)
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
def test_create_crs_and_assign_to_project(setup) -> None:
    user, project = setup
    client = _auth(user)
    created = client.post(
        reverse("gis-crs"),
        {"epsg_code": 4326, "name": "WGS 84"},
        format="json",
    )
    assert created.status_code == status.HTTP_201_CREATED

    assigned = client.post(
        reverse("project-crs", kwargs={"project_id": project.id}),
        {"epsg_code": 4326, "role": "horizontal"},
        format="json",
    )
    assert assigned.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}
    assert assigned.json()["epsg_code"] == 4326


@pytest.mark.django_db
def test_transform_wgs84_to_web_mercator(setup) -> None:
    user, _project = setup
    client = _auth(user)
    response = client.post(
        reverse("gis-transform"),
        {
            "x": 0.0,
            "y": 0.0,
            "source_epsg": 4326,
            "target_epsg": 3857,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert abs(response.json()["x"]) < 1e-6
    assert abs(response.json()["y"]) < 1e-6
