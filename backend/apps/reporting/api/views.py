"""Reporting API views."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.calculations.models import CalculationRun
from apps.projects.models import Project, ProjectMembership, ProjectRole
from apps.reporting.api.serializers import ReportArtifactSerializer, ReportGenerateSerializer
from apps.reporting.models import ReportArtifact
from apps.reporting.services import generate_basic_report


def _project_for_member(user, project_id) -> Project:
    if user.is_superuser:
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
    try:
        return Project.objects.filter(memberships__user=user).distinct().get(id=project_id)
    except Project.DoesNotExist as exc:
        raise NotFound() from exc


def _require_engineer(user, project: Project) -> None:
    if user.is_superuser:
        return
    membership = ProjectMembership.objects.filter(project=project, user=user).first()
    if membership is None or membership.role not in {
        ProjectRole.PROJECT_ADMIN,
        ProjectRole.PROJECT_ENGINEER,
    }:
        raise PermissionDenied("Project admin or engineer role required.")


class ProjectReportListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        artifacts = ReportArtifact.objects.filter(project=project)
        return Response(ReportArtifactSerializer(artifacts, many=True).data)

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = None
        run_id = serializer.validated_data.get("calculation_run_id")
        if run_id:
            try:
                run = CalculationRun.objects.get(id=run_id, project=project)
            except CalculationRun.DoesNotExist as exc:
                raise ValidationError({"calculation_run_id": "Run not found."}) from exc
        artifact = generate_basic_report(
            project=project,
            user=request.user,
            calculation_run=run,
            request=request,
        )
        return Response(
            ReportArtifactSerializer(artifact).data, status=status.HTTP_201_CREATED
        )
