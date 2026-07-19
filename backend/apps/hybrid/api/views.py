"""Hybrid API."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.hybrid.models import HybridCase, hybrid_curtailment_stub, pv_yield_stub
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


class PVYieldView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        results = pv_yield_stub(
            capacity_mw=float(request.data.get("capacity_mw", 0)),
            capacity_factor=float(request.data.get("capacity_factor", 0.18)),
            hours=float(request.data.get("hours", 8760)),
        )
        case = HybridCase.objects.create(
            project=project,
            name=request.data.get("name", "PV yield"),
            method_version=results["method_version"],
            parameters=dict(request.data),
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(case.id), **results}, status=status.HTTP_201_CREATED)


class HybridCurtailmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        wind = request.data.get("wind_mw")
        solar = request.data.get("solar_mw")
        if not isinstance(wind, list) or not isinstance(solar, list):
            raise ValidationError({"detail": "wind_mw and solar_mw lists required"})
        results = hybrid_curtailment_stub(
            wind_mw=[float(x) for x in wind],
            solar_mw=[float(x) for x in solar],
            grid_limit_mw=float(request.data.get("grid_limit_mw", 0)),
        )
        case = HybridCase.objects.create(
            project=project,
            name=request.data.get("name", "Hybrid curtailment"),
            method_version=results["method_version"],
            parameters={
                "grid_limit_mw": request.data.get("grid_limit_mw", 0),
                "steps": len(wind),
            },
            results={k: v for k, v in results.items() if k not in {"delivered_mw", "curtailed_mw"}},
            created_by=request.user,
        )
        return Response({"id": str(case.id), **results}, status=status.HTTP_201_CREATED)
