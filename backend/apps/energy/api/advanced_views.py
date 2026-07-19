"""R4 advanced energy endpoints."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.energy.advanced import jensen_wake_loss_fraction, mcp_linear, uncertainty_p50_p90
from apps.energy.models import EnergyAssessment
from apps.energy.services import EnergyError
from apps.gis.models import TurbinePosition
from apps.projects.models import Project, ProjectMembership, ProjectRole


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


class MCPLinearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        target = request.data.get("target_means")
        reference = request.data.get("reference_means")
        if not isinstance(target, list) or not isinstance(reference, list):
            raise ValidationError({"detail": "target_means and reference_means lists required"})
        try:
            result = mcp_linear(
                target_means=[float(x) for x in target],
                reference_means=[float(x) for x in reference],
            )
        except EnergyError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        record_event(
            action="energy.mcp_linear",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="mcp",
            metadata={"r_squared": result["r_squared"]},
            request=request,
        )
        return Response(result)


class JensenWakeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        wind_dir = float(request.data.get("wind_direction_deg", 0))
        positions = list(
            TurbinePosition.objects.filter(project=project).select_related("turbine_model")
        )
        result = jensen_wake_loss_fraction(positions, wind_direction_deg=wind_dir)
        return Response(result)


class UncertaintyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id, assessment_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        try:
            assessment = EnergyAssessment.objects.get(id=assessment_id, project=project)
        except EnergyAssessment.DoesNotExist as exc:
            raise NotFound() from exc
        u = float(request.data.get("combined_uncertainty", 0.12))
        result = uncertainty_p50_p90(assessment, combined_uncertainty=u)
        assessment.results = {**(assessment.results or {}), "uncertainty": result}
        assessment.save(update_fields=["results"])
        return Response(result, status=status.HTTP_200_OK)
