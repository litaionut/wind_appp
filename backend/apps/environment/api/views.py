"""Environment API."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.environment.models import ImpactRun, Receptor, noise_iso9613_stub, shadow_hours_stub
from apps.gis.models import TurbinePosition
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


class ReceptorListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        data = [
            {"id": str(r.id), "name": r.name, "x": r.x, "y": r.y}
            for r in Receptor.objects.filter(project=project)
        ]
        return Response(data)

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        r = Receptor.objects.create(
            project=project,
            name=request.data["name"],
            x=float(request.data["x"]),
            y=float(request.data["y"]),
        )
        return Response(
            {"id": str(r.id), "name": r.name, "x": r.x, "y": r.y},
            status=status.HTTP_201_CREATED,
        )


class NoiseRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        turbines = list(
            TurbinePosition.objects.filter(project=project).select_related("turbine_model")
        )
        receptors = list(Receptor.objects.filter(project=project))
        results = noise_iso9613_stub(
            turbines, receptors, source_lw_db=float(request.data.get("source_lw_db", 105))
        )
        run = ImpactRun.objects.create(
            project=project,
            name=request.data.get("name", "Noise run"),
            method_version=results["method_version"],
            parameters={"source_lw_db": request.data.get("source_lw_db", 105)},
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(run.id), **results}, status=status.HTTP_201_CREATED)


class ShadowRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        turbines = list(
            TurbinePosition.objects.filter(project=project).select_related("turbine_model")
        )
        receptors = list(Receptor.objects.filter(project=project))
        results = shadow_hours_stub(turbines, receptors)
        run = ImpactRun.objects.create(
            project=project,
            name=request.data.get("name", "Shadow run"),
            method_version=results["method_version"],
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(run.id), **results}, status=status.HTTP_201_CREATED)
