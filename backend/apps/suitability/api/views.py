"""Suitability API."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project, ProjectMembership, ProjectRole
from apps.suitability.models import (
    SuitabilityAssessment,
    iec_class_stub,
    terrain_complexity_stub,
)


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


class IECClassView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        try:
            vave = float(request.data["vave_m_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError({"detail": "vave_m_s required"}) from exc
        results = iec_class_stub(
            vave_m_s=vave,
            vref_m_s=float(request.data["vref_m_s"]) if "vref_m_s" in request.data else None,
            i_ref=float(request.data.get("i_ref", 0.16)),
        )
        run = SuitabilityAssessment.objects.create(
            project=project,
            name=request.data.get("name", "IEC class"),
            method_version=results["method_version"],
            parameters={
                "vave_m_s": vave,
                "vref_m_s": request.data.get("vref_m_s"),
                "i_ref": request.data.get("i_ref", 0.16),
            },
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(run.id), **results}, status=status.HTTP_201_CREATED)


class TerrainComplexityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        results = terrain_complexity_stub(
            elevation_std_m=float(request.data.get("elevation_std_m", 10)),
            slope_deg=float(request.data.get("slope_deg", 2)),
        )
        run = SuitabilityAssessment.objects.create(
            project=project,
            name=request.data.get("name", "Terrain complexity"),
            method_version=results["method_version"],
            parameters={
                "elevation_std_m": request.data.get("elevation_std_m", 10),
                "slope_deg": request.data.get("slope_deg", 2),
            },
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(run.id), **results}, status=status.HTTP_201_CREATED)
