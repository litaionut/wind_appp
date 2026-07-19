"""Project membership management views."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.projects.api.member_serializers import (
    ProjectMembershipCreateSerializer,
    ProjectMembershipSerializer,
)
from apps.projects.models import Project, ProjectMembership, ProjectRole
from apps.projects.services import ProjectMembershipError, ensure_not_last_project_admin


def _get_accessible_project(user, project_id) -> Project:
    if user.is_superuser:
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
    try:
        return Project.objects.filter(memberships__user=user).distinct().get(id=project_id)
    except Project.DoesNotExist as exc:
        raise NotFound() from exc


def _require_project_admin(user, project: Project) -> None:
    if user.is_superuser:
        return
    if not ProjectMembership.objects.filter(
        project=project,
        user=user,
        role=ProjectRole.PROJECT_ADMIN,
    ).exists():
        raise PermissionDenied("You must be a project admin.")


class ProjectMemberListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _get_accessible_project(request.user, project_id)
        memberships = ProjectMembership.objects.filter(project=project).select_related(
            "user"
        )
        return Response(ProjectMembershipSerializer(memberships, many=True).data)

    def post(self, request: Request, project_id) -> Response:
        project = _get_accessible_project(request.user, project_id)
        _require_project_admin(request.user, project)
        serializer = ProjectMembershipCreateSerializer(
            data=request.data,
            context={"project": project},
        )
        serializer.is_valid(raise_exception=True)
        membership = ProjectMembership.objects.create(
            project=project,
            user=serializer.validated_data["user"],
            role=serializer.validated_data["role"],
        )
        record_event(
            action="project.member_added",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="project_membership",
            entity_id=membership.id,
            metadata={
                "username": membership.user.username,
                "role": membership.role,
            },
            request=request,
        )
        return Response(
            ProjectMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


class ProjectMemberDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, project_id, membership_id) -> Response:
        project = _get_accessible_project(request.user, project_id)
        _require_project_admin(request.user, project)
        try:
            membership = ProjectMembership.objects.get(
                id=membership_id, project=project
            )
        except ProjectMembership.DoesNotExist as exc:
            raise NotFound() from exc
        serializer = ProjectMembershipSerializer(
            membership, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        new_role = serializer.validated_data.get("role", membership.role)
        try:
            ensure_not_last_project_admin(membership, new_role=new_role)
        except ProjectMembershipError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        serializer.save()
        record_event(
            action="project.member_role_changed",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="project_membership",
            entity_id=membership.id,
            metadata={
                "username": membership.user.username,
                "role": membership.role,
            },
            request=request,
        )
        return Response(serializer.data)

    def delete(self, request: Request, project_id, membership_id) -> Response:
        project = _get_accessible_project(request.user, project_id)
        _require_project_admin(request.user, project)
        try:
            membership = ProjectMembership.objects.get(
                id=membership_id, project=project
            )
        except ProjectMembership.DoesNotExist as exc:
            raise NotFound() from exc
        try:
            ensure_not_last_project_admin(membership)
        except ProjectMembershipError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        username = membership.user.username
        membership_id_str = str(membership.id)
        membership.delete()
        record_event(
            action="project.member_removed",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="project_membership",
            entity_id=membership_id_str,
            metadata={"username": username},
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
