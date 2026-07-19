"""Project API views."""

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.models import Organization, OrganizationMembership
from apps.projects.api.serializers import ProjectSerializer
from apps.projects.models import Project, ProjectMembership, ProjectRole
from apps.projects.permissions import IsProjectAdminOrReadMember


def _org_for_member(user, org_id) -> Organization:
    if user.is_superuser:
        try:
            return Organization.objects.get(id=org_id)
        except Organization.DoesNotExist as exc:
            raise NotFound() from exc
    try:
        return Organization.objects.filter(memberships__user=user).distinct().get(id=org_id)
    except Organization.DoesNotExist as exc:
        raise NotFound() from exc


class OrganizationProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, org_id) -> Response:
        organization = _org_for_member(request.user, org_id)
        if request.user.is_superuser:
            projects = Project.objects.filter(organization=organization)
        else:
            projects = Project.objects.filter(
                organization=organization,
                memberships__user=request.user,
            ).distinct()
        return Response(ProjectSerializer(projects, many=True).data)

    @transaction.atomic
    def post(self, request: Request, org_id) -> Response:
        organization = _org_for_member(request.user, org_id)
        if not request.user.is_superuser and not OrganizationMembership.objects.filter(
            organization=organization, user=request.user
        ).exists():
            raise PermissionDenied("You must be an organization member.")
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save(organization=organization, created_by=request.user)
        ProjectMembership.objects.create(
            project=project,
            user=request.user,
            role=ProjectRole.PROJECT_ADMIN,
        )
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadMember]

    def get_object(self, request: Request, project_id) -> Project:
        qs = Project.objects.all()
        if not request.user.is_superuser:
            qs = qs.filter(memberships__user=request.user).distinct()
        try:
            project = qs.get(id=project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        self.check_object_permissions(request, project)
        return project

    def get(self, request: Request, project_id) -> Response:
        project = self.get_object(request, project_id)
        return Response(ProjectSerializer(project).data)

    def patch(self, request: Request, project_id) -> Response:
        project = self.get_object(request, project_id)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
