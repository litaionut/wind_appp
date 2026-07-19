"""Organization API views."""

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.audit.services import record_event
from apps.organizations.api.serializers import OrganizationSerializer
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.organizations.permissions import IsOrganizationAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    """CRUD for organizations (no destroy in this increment)."""

    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    http_method_names = ["get", "post", "patch", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(memberships__user=user).distinct()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrganizationAdmin()]

    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = serializer.save(created_by=request.user)
        OrganizationMembership.objects.create(
            organization=organization,
            user=request.user,
            role=OrganizationRole.ORG_ADMIN,
        )
        record_event(
            action="organization.created",
            actor=request.user,
            organization=organization,
            entity_type="organization",
            entity_id=organization.id,
            metadata={"name": organization.name},
            request=request,
        )
        return Response(
            self.get_serializer(organization).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_update(self, serializer) -> None:
        organization = serializer.save()
        record_event(
            action="organization.updated",
            actor=self.request.user,
            organization=organization,
            entity_type="organization",
            entity_id=organization.id,
            metadata={"name": organization.name},
            request=self.request,
        )
