"""METEO foundation tests."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="meteo_user", password="pass-meteo-1")
    org = Organization.objects.create(name="Meteo Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Meteo Project", created_by=user)
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
def test_meteo_campaign_import_rose_density(setup) -> None:
    user, project = setup
    client = _auth(user)

    campaign = client.post(
        reverse("project-meteo-campaigns", kwargs={"project_id": project.id}),
        {"name": "Mast A", "structure_type": "mast", "latitude": 45.0, "longitude": 25.0},
        format="json",
    )
    assert campaign.status_code == status.HTTP_201_CREATED
    cid = campaign.json()["id"]

    for payload in (
        {"code": "WS80", "variable": "wind_speed", "height_m": 80, "unit": "m/s"},
        {"code": "WD80", "variable": "wind_direction", "height_m": 80, "unit": "deg"},
        {"code": "T10", "variable": "temperature", "height_m": 10, "unit": "degC"},
        {"code": "P10", "variable": "pressure", "height_m": 10, "unit": "hPa"},
    ):
        resp = client.post(
            reverse("meteo-campaign-sensors", kwargs={"campaign_id": cid}),
            payload,
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED

    csv_body = "\n".join(
        [
            "timestamp,sensor_code,value",
            "2024-01-01T00:00:00Z,WS80,8.0",
            "2024-01-01T00:00:00Z,WD80,45",
            "2024-01-01T00:00:00Z,T10,15",
            "2024-01-01T00:00:00Z,P10,1013",
            "2024-01-01T00:10:00Z,WS80,9.0",
            "2024-01-01T00:10:00Z,WD80,50",
            "2024-01-01T00:10:00Z,T10,15",
            "2024-01-01T00:10:00Z,P10,1013",
            "2024-01-01T00:20:00Z,WS80,",
            "2024-01-01T00:20:00Z,WD80,55",
        ]
    )
    imported = client.post(
        reverse("meteo-timeseries-import", kwargs={"campaign_id": cid}),
        {
            "file": SimpleUploadedFile(
                "ts.csv", csv_body.encode(), content_type="text/csv"
            )
        },
        format="multipart",
    )
    assert imported.status_code == status.HTTP_200_OK
    assert imported.json()["created"] == 10

    availability = client.get(reverse("meteo-availability", kwargs={"campaign_id": cid}))
    assert availability.status_code == status.HTTP_200_OK
    assert availability.json()["total_points"] == 10
    assert availability.json()["flags"].get("missing") == 1

    rose = client.get(
        reverse("meteo-wind-rose", kwargs={"campaign_id": cid}),
        {"speed_code": "WS80", "direction_code": "WD80"},
    )
    assert rose.status_code == status.HTTP_200_OK
    assert rose.json()["paired_samples"] == 2

    density = client.get(
        reverse("meteo-air-density", kwargs={"campaign_id": cid}),
        {"temperature_code": "T10", "pressure_code": "P10"},
    )
    assert density.status_code == status.HTTP_200_OK
    assert density.json()["samples"] == 2
    # ~1.225 kg/m3 at 15C / 1013 hPa
    assert density.json()["mean_air_density_kg_m3"] == pytest.approx(1.225, abs=0.02)
