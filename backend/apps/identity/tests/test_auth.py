"""Tests for authentication API."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(username="engineer", password="secure-pass-123")


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_login_returns_token(api_client: APIClient, user: User) -> None:
    response = api_client.post(
        reverse("auth-login"),
        {"username": "engineer", "password": "secure-pass-123"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.json()
    assert Token.objects.filter(user=user, key=response.json()["token"]).exists()


@pytest.mark.django_db
def test_login_invalid_credentials(api_client: APIClient, user: User) -> None:
    response = api_client.post(
        reverse("auth-login"),
        {"username": "engineer", "password": "wrong-password"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_requires_authentication(api_client: APIClient) -> None:
    response = api_client.get(reverse("auth-me"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_returns_user(api_client: APIClient, user: User) -> None:
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    response = api_client.get(reverse("auth-me"))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": user.id,
        "username": "engineer",
        "email": "",
        "is_staff": False,
    }


@pytest.mark.django_db
def test_logout_revokes_token(api_client: APIClient, user: User) -> None:
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    response = api_client.post(reverse("auth-logout"))
    assert response.status_code == status.HTTP_200_OK
    assert not Token.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_inactive_user_cannot_login(api_client: APIClient) -> None:
    User.objects.create_user(
        username="disabled",
        password="secure-pass-123",
        is_active=False,
    )
    response = api_client.post(
        reverse("auth-login"),
        {"username": "disabled", "password": "secure-pass-123"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_health_remains_public(api_client: APIClient) -> None:
    response = api_client.get(reverse("health"))
    assert response.status_code == status.HTTP_200_OK
