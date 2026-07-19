"""Tests for the health-check endpoint."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


def test_health_returns_200() -> None:
    client = APIClient()
    response = client.get(reverse("health"))
    assert response.status_code == status.HTTP_200_OK


def test_health_body_status_ok() -> None:
    client = APIClient()
    response = client.get("/api/v1/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
        "service": "wind-platform-api",
        "api_version": "v1",
    }
