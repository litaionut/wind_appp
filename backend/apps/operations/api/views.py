"""Operations API."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.operations.models import OperationsSnapshot, availability_kpi
from apps.projects.models import Project, ProjectMembership, ProjectRole


def _project(user, project_id) -> Project:
    if user.is_superuser:
        return Project.objects.get(id=project_id)
    return Project.objects.filter(memberships__user=user).distinct().get(id=project_id)


def _eng(user, project: Project) -> None:
    if user.is_superuser:
        return
    m = ProjectMembership.objects.filter(project=project, user=user).first()
    if m is None or m.role not in {ProjectRole.PROJECT_ADMIN, ProjectRole.PROJECT_ENGINEER}:
        raise PermissionDenied("Project admin or engineer role required.")


class AvailabilityKPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        results = availability_kpi(
            period_hours=float(request.data.get("period_hours", 8760)),
            downtime_hours=float(request.data.get("downtime_hours", 0)),
            energy_produced_mwh=float(request.data.get("energy_produced_mwh", 0)),
            energy_expected_mwh=float(request.data.get("energy_expected_mwh", 0)),
        )
        snap = OperationsSnapshot.objects.create(
            project=project,
            name=request.data.get("name", "Availability KPI"),
            method_version=results["method_version"],
            parameters={
                "period_hours": request.data.get("period_hours", 8760),
                "downtime_hours": request.data.get("downtime_hours", 0),
                "energy_produced_mwh": request.data.get("energy_produced_mwh", 0),
                "energy_expected_mwh": request.data.get("energy_expected_mwh", 0),
            },
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(snap.id), **results}, status=status.HTTP_201_CREATED)
