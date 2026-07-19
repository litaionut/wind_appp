"""Tests for organization API isolation."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_a(db) -> User:
    return User.objects.create_user(username="alice", password="pass-alice-123")


@pytest.fixture
def user_b(db) -> User:
    return User.objects.create_user(username="bob", password="pass-bob-123")


def _auth(client: APIClient, user: User) -> APIClient:
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_create_organization_makes_creator_admin(api_client: APIClient, user_a: User) -> None:
    client = _auth(api_client, user_a)
    response = client.post(
        reverse("organization-list"),
        {"name": "Wind Co"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    org_id = response.json()["id"]
    assert response.json()["slug"] == "wind-co"
    assert OrganizationMembership.objects.filter(
        organization_id=org_id,
        user=user_a,
        role=OrganizationRole.ORG_ADMIN,
    ).exists()


@pytest.mark.django_db
def test_list_only_returns_member_organizations(
    api_client: APIClient, user_a: User, user_b: User
) -> None:
    org_a = Organization.objects.create(name="Org A", created_by=user_a)
    org_b = Organization.objects.create(name="Org B", created_by=user_b)
    OrganizationMembership.objects.create(
        organization=org_a, user=user_a, role=OrganizationRole.ORG_ADMIN
    )
    OrganizationMembership.objects.create(
        organization=org_b, user=user_b, role=OrganizationRole.ORG_ADMIN
    )

    client = _auth(api_client, user_a)
    response = client.get(reverse("organization-list"))
    assert response.status_code == status.HTTP_200_OK
    ids = {item["id"] for item in response.json()}
    assert ids == {str(org_a.id)}


@pytest.mark.django_db
def test_non_member_cannot_retrieve(
    api_client: APIClient, user_a: User, user_b: User
) -> None:
    org = Organization.objects.create(name="Secret Org", created_by=user_a)
    OrganizationMembership.objects.create(
        organization=org, user=user_a, role=OrganizationRole.ORG_ADMIN
    )

    client = _auth(api_client, user_b)
    response = client.get(reverse("organization-detail", kwargs={"id": org.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_member_cannot_update_without_admin_role(
    api_client: APIClient, user_a: User, user_b: User
) -> None:
    org = Organization.objects.create(name="Shared Org", created_by=user_a)
    OrganizationMembership.objects.create(
        organization=org, user=user_a, role=OrganizationRole.ORG_ADMIN
    )
    OrganizationMembership.objects.create(
        organization=org, user=user_b, role=OrganizationRole.ORG_MEMBER
    )

    client = _auth(api_client, user_b)
    response = client.patch(
        reverse("organization-detail", kwargs={"id": org.id}),
        {"name": "Hijacked"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_org_admin_can_update(api_client: APIClient, user_a: User) -> None:
    org = Organization.objects.create(name="Editable", created_by=user_a)
    OrganizationMembership.objects.create(
        organization=org, user=user_a, role=OrganizationRole.ORG_ADMIN
    )

    client = _auth(api_client, user_a)
    response = client.patch(
        reverse("organization-detail", kwargs={"id": org.id}),
        {"name": "Edited Name"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Edited Name"


@pytest.mark.django_db
def test_unauthenticated_cannot_list(api_client: APIClient) -> None:
    response = api_client.get(reverse("organization-list"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
