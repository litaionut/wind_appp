"""Organization membership management views."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.organizations.api.member_serializers import (
    OrganizationMembershipCreateSerializer,
    OrganizationMembershipSerializer,
)
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.organizations.services import MembershipError, ensure_not_last_admin


def _get_accessible_org(user, org_id) -> Organization:
    if user.is_superuser:
        try:
            return Organization.objects.get(id=org_id)
        except Organization.DoesNotExist as exc:
            raise NotFound() from exc
    try:
        return Organization.objects.filter(memberships__user=user).distinct().get(id=org_id)
    except Organization.DoesNotExist as exc:
        raise NotFound() from exc


def _require_org_admin(user, organization: Organization) -> None:
    if user.is_superuser:
        return
    if not OrganizationMembership.objects.filter(
        organization=organization,
        user=user,
        role=OrganizationRole.ORG_ADMIN,
    ).exists():
        raise PermissionDenied("You must be an organization admin.")


class OrganizationMemberListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, org_id) -> Response:
        organization = _get_accessible_org(request.user, org_id)
        memberships = OrganizationMembership.objects.filter(
            organization=organization
        ).select_related("user")
        return Response(OrganizationMembershipSerializer(memberships, many=True).data)

    def post(self, request: Request, org_id) -> Response:
        organization = _get_accessible_org(request.user, org_id)
        _require_org_admin(request.user, organization)
        serializer = OrganizationMembershipCreateSerializer(
            data=request.data,
            context={"organization": organization},
        )
        serializer.is_valid(raise_exception=True)
        membership = OrganizationMembership.objects.create(
            organization=organization,
            user=serializer.validated_data["user"],
            role=serializer.validated_data["role"],
        )
        record_event(
            action="organization.member_added",
            actor=request.user,
            organization=organization,
            entity_type="organization_membership",
            entity_id=membership.id,
            metadata={
                "username": membership.user.username,
                "role": membership.role,
            },
            request=request,
        )
        return Response(
            OrganizationMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


class OrganizationMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, org_id, membership_id) -> Response:
        organization = _get_accessible_org(request.user, org_id)
        _require_org_admin(request.user, organization)
        try:
            membership = OrganizationMembership.objects.get(
                id=membership_id, organization=organization
            )
        except OrganizationMembership.DoesNotExist as exc:
            raise NotFound() from exc

        serializer = OrganizationMembershipSerializer(
            membership, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        new_role = serializer.validated_data.get("role", membership.role)
        try:
            ensure_not_last_admin(membership, new_role=new_role)
        except MembershipError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        serializer.save()
        record_event(
            action="organization.member_role_changed",
            actor=request.user,
            organization=organization,
            entity_type="organization_membership",
            entity_id=membership.id,
            metadata={
                "username": membership.user.username,
                "role": membership.role,
            },
            request=request,
        )
        return Response(serializer.data)

    def delete(self, request: Request, org_id, membership_id) -> Response:
        organization = _get_accessible_org(request.user, org_id)
        _require_org_admin(request.user, organization)
        try:
            membership = OrganizationMembership.objects.get(
                id=membership_id, organization=organization
            )
        except OrganizationMembership.DoesNotExist as exc:
            raise NotFound() from exc
        try:
            ensure_not_last_admin(membership)
        except MembershipError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        username = membership.user.username
        membership_id_str = str(membership.id)
        membership.delete()
        record_event(
            action="organization.member_removed",
            actor=request.user,
            organization=organization,
            entity_type="organization_membership",
            entity_id=membership_id_str,
            metadata={"username": username},
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
