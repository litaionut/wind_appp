"""Calculation method and run APIs."""

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.calculations.api.serializers import (
    CalculationLogSerializer,
    CalculationMethodSerializer,
    CalculationRunCreateSerializer,
    CalculationRunSerializer,
)
from apps.calculations.executor import execute_run
from apps.calculations.models import CalculationMethod, CalculationRun
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


class CalculationMethodListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        methods = CalculationMethod.objects.all()
        return Response(CalculationMethodSerializer(methods, many=True).data)


class ProjectCalculationRunListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        runs = CalculationRun.objects.filter(project=project).select_related("method")
        return Response(CalculationRunSerializer(runs, many=True).data)

    @transaction.atomic
    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        serializer = CalculationRunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            method = CalculationMethod.objects.get(
                method_id=data["method_id"], version=data["method_version"]
            )
        except CalculationMethod.DoesNotExist as exc:
            raise ValidationError({"method_id": "Unknown method/version."}) from exc

        calculation_type = data.get("calculation_type") or method.method_id
        run = CalculationRun.objects.create(
            organization=project.organization,
            project=project,
            method=method,
            calculation_type=calculation_type,
            application_version=getattr(settings, "APPLICATION_VERSION", "0.2.0"),
            parameters=data.get("parameters") or {},
            assumptions=data.get("assumptions") or {},
            input_data_version=data.get("input_data_version") or "",
            created_by=request.user,
        )
        if data.get("execute", True):
            execute_run(run)
        record_event(
            action="calculation_run.created",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="calculation_run",
            entity_id=run.id,
            metadata={
                "method": method.registry_key,
                "status": run.status,
            },
            request=request,
        )
        return Response(
            CalculationRunSerializer(run).data, status=status.HTTP_201_CREATED
        )


class CalculationRunDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, run_id) -> Response:
        run = _run_for_member(request.user, run_id)
        return Response(CalculationRunSerializer(run).data)


class CalculationRunLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, run_id) -> Response:
        run = _run_for_member(request.user, run_id)
        return Response(CalculationLogSerializer(run.logs.all(), many=True).data)


def _run_for_member(user, run_id) -> CalculationRun:
    try:
        run = CalculationRun.objects.select_related("project", "method").get(id=run_id)
    except CalculationRun.DoesNotExist as exc:
        raise NotFound() from exc
    if user.is_superuser:
        return run
    if not ProjectMembership.objects.filter(project=run.project, user=user).exists():
        raise NotFound()
    return run
