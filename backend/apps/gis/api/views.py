"""GIS CRS and transform APIs."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.gis.api.serializers import (
    CRSSerializer,
    ProjectCRSAssignSerializer,
    ProjectCRSSerializer,
    TransformSerializer,
)
from apps.gis.models import CoordinateReferenceSystem, ProjectCRS
from apps.gis.transforms import TransformError, transform_xy
from apps.projects.models import Project, ProjectMembership, ProjectRole


class CRSListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(
            CRSSerializer(CoordinateReferenceSystem.objects.all(), many=True).data
        )

    def post(self, request: Request) -> Response:
        serializer = CRSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        crs = serializer.save()
        return Response(CRSSerializer(crs).data, status=status.HTTP_201_CREATED)


class ProjectCRSListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        links = ProjectCRS.objects.filter(project=project).select_related("crs")
        return Response(ProjectCRSSerializer(links, many=True).data)

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_project_admin(request.user, project)
        serializer = ProjectCRSAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        name = data.get("name") or f"EPSG:{data['epsg_code']}"
        crs, _ = CoordinateReferenceSystem.objects.get_or_create(
            epsg_code=data["epsg_code"],
            defaults={"name": name},
        )
        link, created = ProjectCRS.objects.update_or_create(
            project=project,
            role=data["role"],
            defaults={"crs": crs},
        )
        record_event(
            action="project.crs_assigned",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="project_crs",
            entity_id=link.id,
            metadata={"epsg_code": crs.epsg_code, "role": link.role},
            request=request,
        )
        return Response(
            ProjectCRSSerializer(link).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TransformView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = TransformSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            x2, y2 = transform_xy(
                x=data["x"],
                y=data["y"],
                source_epsg=data["source_epsg"],
                target_epsg=data["target_epsg"],
            )
        except TransformError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        return Response(
            {
                "x": x2,
                "y": y2,
                "source_epsg": data["source_epsg"],
                "target_epsg": data["target_epsg"],
                "unit_note": "Output coordinates are in the target CRS axis units.",
            }
        )


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


def _require_project_admin(user, project: Project) -> None:
    if user.is_superuser:
        return
    if not ProjectMembership.objects.filter(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    ).exists():
        raise PermissionDenied("Project admin role required.")
