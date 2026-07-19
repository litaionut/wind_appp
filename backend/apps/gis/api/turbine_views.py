"""Turbine catalogue, positions, and distance APIs."""

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.gis.api.turbine_serializers import (
    TurbineManufacturerSerializer,
    TurbineModelSerializer,
    TurbinePositionSerializer,
    TurbinePositionWriteSerializer,
)
from apps.gis.catalogue_import import ImportErrorDetail, import_catalogue_csv, import_positions_csv
from apps.gis.distances import pairwise_distances
from apps.gis.models import (
    ProjectCRS,
    ProjectCRSRole,
    TurbineManufacturer,
    TurbineModel,
    TurbinePosition,
)
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


class TurbineModelListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        models_qs = TurbineModel.objects.select_related("manufacturer")
        return Response(TurbineModelSerializer(models_qs, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = TurbineModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model = serializer.save()
        record_event(
            action="turbine_model.created",
            actor=request.user,
            entity_type="turbine_model",
            entity_id=model.id,
            metadata={"name": str(model)},
            request=request,
        )
        return Response(TurbineModelSerializer(model).data, status=status.HTTP_201_CREATED)


class TurbineManufacturerListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        qs = TurbineManufacturer.objects.all()
        return Response(TurbineManufacturerSerializer(qs, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = TurbineManufacturerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mfr = serializer.save()
        return Response(
            TurbineManufacturerSerializer(mfr).data, status=status.HTTP_201_CREATED
        )


class TurbineCatalogueImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "This field is required."})
        text = upload.read().decode("utf-8-sig")
        try:
            result = import_catalogue_csv(text)
        except ImportErrorDetail as exc:
            raise ValidationError({"detail": exc.message}) from exc
        record_event(
            action="turbine_catalogue.imported",
            actor=request.user,
            entity_type="turbine_catalogue",
            metadata=result,
            request=request,
        )
        return Response(result, status=status.HTTP_200_OK)


class ProjectTurbineListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        positions = TurbinePosition.objects.filter(project=project).select_related(
            "turbine_model", "crs"
        )
        return Response(TurbinePositionSerializer(positions, many=True).data)

    @transaction.atomic
    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        serializer = TurbinePositionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crs = None
        link = ProjectCRS.objects.filter(
            project=project, role=ProjectCRSRole.HORIZONTAL
        ).select_related("crs").first()
        if link:
            crs = link.crs
        position = serializer.save(project=project, created_by=request.user, crs=crs)
        record_event(
            action="turbine_position.created",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="turbine_position",
            entity_id=position.id,
            metadata={"label": position.label},
            request=request,
        )
        return Response(
            TurbinePositionSerializer(position).data, status=status.HTTP_201_CREATED
        )


class ProjectTurbineImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "This field is required."})
        text = upload.read().decode("utf-8-sig")
        try:
            result = import_positions_csv(project=project, text=text, user=request.user)
        except ImportErrorDetail as exc:
            raise ValidationError({"detail": exc.message}) from exc
        record_event(
            action="turbine_positions.imported",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="turbine_position",
            metadata=result,
            request=request,
        )
        return Response(result, status=status.HTTP_200_OK)


class ProjectTurbineDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, project_id, turbine_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        try:
            position = TurbinePosition.objects.get(id=turbine_id, project=project)
        except TurbinePosition.DoesNotExist as exc:
            raise NotFound() from exc
        serializer = TurbinePositionWriteSerializer(
            position, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        position = serializer.save()
        return Response(TurbinePositionSerializer(position).data)

    def delete(self, request: Request, project_id, turbine_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        try:
            position = TurbinePosition.objects.get(id=turbine_id, project=project)
        except TurbinePosition.DoesNotExist as exc:
            raise NotFound() from exc
        label = position.label
        position.delete()
        record_event(
            action="turbine_position.deleted",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="turbine_position",
            entity_id=turbine_id,
            metadata={"label": label},
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectTurbineDistancesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        positions = list(
            TurbinePosition.objects.filter(project=project)
            .select_related("crs", "project")
            .order_by("label")
        )
        pairs = pairwise_distances(positions)
        return Response(
            {
                "count": len(pairs),
                "pairs": [
                    {
                        "from_label": p.from_label,
                        "to_label": p.to_label,
                        "from_id": p.from_id,
                        "to_id": p.to_id,
                        "distance_m": p.distance_m,
                        "unit": "m",
                        "method": p.method,
                    }
                    for p in pairs
                ],
            }
        )
