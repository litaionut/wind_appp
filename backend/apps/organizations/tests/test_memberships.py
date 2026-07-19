"""Tests for organization membership management API."""

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
def admin_user(db) -> User:
    return User.objects.create_user(username="admin_user", password="pass-admin-123")


@pytest.fixture
def member_user(db) -> User:
    return User.objects.create_user(username="member_user", password="pass-member-123")


@pytest.fixture
def outsider(db) -> User:
    return User.objects.create_user(username="outsider", password="pass-out-123")


@pytest.fixture
def org_with_admin(admin_user: User) -> tuple[Organization, OrganizationMembership]:
    org = Organization.objects.create(name="Member Org", created_by=admin_user)
    membership = OrganizationMembership.objects.create(
        organization=org,
        user=admin_user,
        role=OrganizationRole.ORG_ADMIN,
    )
    return org, membership


def _auth(client: APIClient, user: User) -> APIClient:
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_admin_can_add_member(
    api_client: APIClient,
    admin_user: User,
    member_user: User,
    org_with_admin: tuple[Organization, OrganizationMembership],
) -> None:
    org, _ = org_with_admin
    client = _auth(api_client, admin_user)
    response = client.post(
        reverse("organization-members", kwargs={"org_id": org.id}),
        {"username": "member_user", "role": "org_member"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "member_user"
    assert OrganizationMembership.objects.filter(
        organization=org, user=member_user
    ).exists()


@pytest.mark.django_db
def test_member_cannot_add_member(
    api_client: APIClient,
    admin_user: User,
    member_user: User,
    outsider: User,
    org_with_admin: tuple[Organization, OrganizationMembership],
) -> None:
    org, _ = org_with_admin
    OrganizationMembership.objects.create(
        organization=org, user=member_user, role=OrganizationRole.ORG_MEMBER
    )
    client = _auth(api_client, member_user)
    response = client.post(
        reverse("organization-members", kwargs={"org_id": org.id}),
        {"username": "outsider", "role": "org_member"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cannot_remove_last_admin(
    api_client: APIClient,
    admin_user: User,
    org_with_admin: tuple[Organization, OrganizationMembership],
) -> None:
    org, membership = org_with_admin
    client = _auth(api_client, admin_user)
    response = client.delete(
        reverse(
            "organization-member-detail",
            kwargs={"org_id": org.id, "membership_id": membership.id},
        )
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_admin_can_change_role(
    api_client: APIClient,
    admin_user: User,
    member_user: User,
    org_with_admin: tuple[Organization, OrganizationMembership],
) -> None:
    org, _ = org_with_admin
    membership = OrganizationMembership.objects.create(
        organization=org, user=member_user, role=OrganizationRole.ORG_MEMBER
    )
    client = _auth(api_client, admin_user)
    response = client.patch(
        reverse(
            "organization-member-detail",
            kwargs={"org_id": org.id, "membership_id": membership.id},
        ),
        {"role": "org_auditor"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "org_auditor"


@pytest.mark.django_db
def test_outsider_cannot_list_members(
    api_client: APIClient,
    outsider: User,
    org_with_admin: tuple[Organization, OrganizationMembership],
) -> None:
    org, _ = org_with_admin
    client = _auth(api_client, outsider)
    response = client.get(reverse("organization-members", kwargs={"org_id": org.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
