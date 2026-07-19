"""Energy assessment APIs."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.energy.api.serializers import (
    CtCurveSerializer,
    EnergyAssessmentSerializer,
    PowerCurveSerializer,
)
from apps.energy.models import CtCurve, EnergyAssessment, PowerCurve
from apps.energy.services import (
    EnergyError,
    calculate_gross_energy,
    import_ct_curve_csv,
    import_power_curve_csv,
)
from apps.gis.models import TurbineModel
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


class PowerCurveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        qs = PowerCurve.objects.select_related("turbine_model").prefetch_related("points")
        return Response(PowerCurveSerializer(qs, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = PowerCurveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not TurbineModel.objects.filter(
            id=serializer.validated_data["turbine_model"].id
        ).exists():
            raise ValidationError({"turbine_model": "Not found."})
        curve = serializer.save()
        return Response(PowerCurveSerializer(curve).data, status=status.HTTP_201_CREATED)


class PowerCurveImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request, curve_id) -> Response:
        try:
            curve = PowerCurve.objects.get(id=curve_id)
        except PowerCurve.DoesNotExist as exc:
            raise NotFound() from exc
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "This field is required."})
        try:
            result = import_power_curve_csv(curve, upload.read().decode("utf-8-sig"))
        except EnergyError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        return Response(result)


class CtCurveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        qs = CtCurve.objects.select_related("turbine_model").prefetch_related("points")
        return Response(CtCurveSerializer(qs, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = CtCurveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not TurbineModel.objects.filter(
            id=serializer.validated_data["turbine_model"].id
        ).exists():
            raise ValidationError({"turbine_model": "Not found."})
        curve = serializer.save()
        return Response(CtCurveSerializer(curve).data, status=status.HTTP_201_CREATED)


class CtCurveImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request, curve_id) -> Response:
        try:
            curve = CtCurve.objects.get(id=curve_id)
        except CtCurve.DoesNotExist as exc:
            raise NotFound() from exc
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "This field is required."})
        try:
            result = import_ct_curve_csv(curve, upload.read().decode("utf-8-sig"))
        except EnergyError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        return Response(result)


class ProjectEnergyAssessmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        qs = EnergyAssessment.objects.filter(project=project)
        return Response(EnergyAssessmentSerializer(qs, many=True).data)

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        serializer = EnergyAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assessment = serializer.save(
            project=project, created_by=request.user, method_version="gross_energy_v1"
        )
        try:
            results = calculate_gross_energy(assessment)
        except EnergyError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        record_event(
            action="energy.assessment_created",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="energy_assessment",
            entity_id=assessment.id,
            metadata={
                "plant_net_aep_mwh": results["plant_net_aep_mwh"],
                "method_version": results["method_version"],
            },
            request=request,
        )
        return Response(
            EnergyAssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED
        )
