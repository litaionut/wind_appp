"""Financial API."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.financial.models import FinancialCase, electrical_loss_stub, lcoe_npv_stub
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


class ElectricalLossView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        results = electrical_loss_stub(
            gross_aep_mwh=float(request.data.get("gross_aep_mwh", 0)),
            cable_loss_fraction=float(request.data.get("cable_loss_fraction", 0.02)),
            transformer_loss_fraction=float(
                request.data.get("transformer_loss_fraction", 0.01)
            ),
        )
        case = FinancialCase.objects.create(
            project=project,
            name=request.data.get("name", "Electrical losses"),
            method_version=results["method_version"],
            parameters=dict(request.data),
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(case.id), **results}, status=status.HTTP_201_CREATED)


class LCOENPVView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        try:
            project = _project(request.user, project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
        _eng(request.user, project)
        results = lcoe_npv_stub(
            annual_energy_mwh=float(request.data.get("annual_energy_mwh", 0)),
            capex=float(request.data.get("capex", 0)),
            opex_annual=float(request.data.get("opex_annual", 0)),
            lifetime_years=int(request.data.get("lifetime_years", 25)),
            discount_rate=float(request.data.get("discount_rate", 0.07)),
            price_per_mwh=float(request.data.get("price_per_mwh", 50)),
        )
        case = FinancialCase.objects.create(
            project=project,
            name=request.data.get("name", "LCOE/NPV"),
            method_version=results["method_version"],
            parameters=dict(request.data),
            results=results,
            created_by=request.user,
        )
        return Response({"id": str(case.id), **results}, status=status.HTTP_201_CREATED)
