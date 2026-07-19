"""Audit read APIs."""

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.api.serializers import AuditEventSerializer
from apps.audit.models import AuditEvent
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


class OrganizationAuditEventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, org_id) -> Response:
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist as exc:
            raise NotFound() from exc

        if not request.user.is_superuser:
            membership = OrganizationMembership.objects.filter(
                organization=organization, user=request.user
            ).first()
            if membership is None:
                raise NotFound()
            if membership.role not in {
                OrganizationRole.ORG_ADMIN,
                OrganizationRole.ORG_AUDITOR,
            }:
                raise PermissionDenied("Organization admin or auditor role required.")

        events = AuditEvent.objects.filter(organization=organization).select_related(
            "actor"
        )[:200]
        return Response(AuditEventSerializer(events, many=True).data)


class ProjectAuditEventListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc

        if not request.user.is_superuser:
            membership = ProjectMembership.objects.filter(
                project=project, user=request.user
            ).first()
            if membership is None:
                raise NotFound()
            if membership.role != ProjectRole.PROJECT_ADMIN:
                raise PermissionDenied("Project admin role required.")

        events = AuditEvent.objects.filter(project=project).select_related("actor")[:200]
        return Response(AuditEventSerializer(events, many=True).data)
