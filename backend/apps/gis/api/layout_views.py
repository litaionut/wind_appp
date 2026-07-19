"""Spacing, boundaries, validation, and GeoJSON export."""

from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.gis.models import BoundaryKind, ProjectBoundary, TurbinePosition
from apps.gis.spacing import check_directional_spacing
from apps.gis.spatial_validation import point_in_polygon
from apps.projects.models import Project, ProjectMembership, ProjectRole


class SpacingCheckSerializer(serializers.Serializer):
    wind_direction_deg = serializers.FloatField(min_value=0.0, max_value=360.0)
    sector_half_width_deg = serializers.FloatField(
        required=False, default=30.0, min_value=0.0
    )
    min_downstream_rd = serializers.FloatField(required=False, default=5.0, min_value=0.0)
    min_crosswind_rd = serializers.FloatField(required=False, default=3.0, min_value=0.0)
    default_rotor_diameter_m = serializers.FloatField(
        required=False, default=150.0, min_value=1.0
    )


class BoundarySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    kind = serializers.ChoiceField(choices=BoundaryKind.choices)
    geometry = serializers.JSONField()
    created_at = serializers.CharField(read_only=True)


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


class ProjectSpacingCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        serializer = SpacingCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        positions = list(
            TurbinePosition.objects.filter(project=project).select_related("turbine_model")
        )
        violations = check_directional_spacing(positions, **data)
        return Response(
            {
                "turbine_count": len(positions),
                "violation_count": len(violations),
                "violations": [
                    {
                        "from_label": v.from_label,
                        "to_label": v.to_label,
                        "distance_m": v.distance_m,
                        "required_m": v.required_m,
                        "direction_deg": v.direction_deg,
                        "rotor_diameters": v.rotor_diameters,
                        "unit": "m",
                    }
                    for v in violations
                ],
            }
        )


class ProjectBoundaryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        items = ProjectBoundary.objects.filter(project=project)
        return Response(
            [
                {
                    "id": str(b.id),
                    "name": b.name,
                    "kind": b.kind,
                    "geometry": b.geometry,
                    "created_at": b.created_at.isoformat(),
                }
                for b in items
            ]
        )

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        serializer = BoundarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        geometry = serializer.validated_data["geometry"]
        if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            raise ValidationError({"geometry": "Must be Polygon or MultiPolygon GeoJSON."})
        boundary = ProjectBoundary.objects.create(
            project=project,
            name=serializer.validated_data["name"],
            kind=serializer.validated_data["kind"],
            geometry=geometry,
            created_by=request.user,
        )
        record_event(
            action="project_boundary.created",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="project_boundary",
            entity_id=boundary.id,
            metadata={"kind": boundary.kind, "name": boundary.name},
            request=request,
        )
        return Response(
            {
                "id": str(boundary.id),
                "name": boundary.name,
                "kind": boundary.kind,
                "geometry": boundary.geometry,
                "created_at": boundary.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class ProjectSpatialValidationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        boundaries = list(
            ProjectBoundary.objects.filter(
                project=project, kind=BoundaryKind.PROJECT_BOUNDARY
            )
        )
        exclusions = list(
            ProjectBoundary.objects.filter(
                project=project, kind=BoundaryKind.EXCLUSION_ZONE
            )
        )
        positions = list(TurbinePosition.objects.filter(project=project))
        issues = []
        for pos in positions:
            if boundaries:
                inside_any = any(
                    point_in_polygon(pos.x, pos.y, b.geometry) for b in boundaries
                )
                if not inside_any:
                    issues.append(
                        {
                            "label": pos.label,
                            "code": "outside_boundary",
                            "message": "Turbine is outside project boundary.",
                        }
                    )
            for ex in exclusions:
                if point_in_polygon(pos.x, pos.y, ex.geometry):
                    issues.append(
                        {
                            "label": pos.label,
                            "code": "inside_exclusion",
                            "message": f"Turbine is inside exclusion zone '{ex.name}'.",
                        }
                    )
        return Response({"issue_count": len(issues), "issues": issues})


class ProjectLayoutGeoJSONView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        turbines = TurbinePosition.objects.filter(project=project)
        boundaries = ProjectBoundary.objects.filter(project=project)
        features = []
        for t in turbines:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [t.x, t.y]},
                    "properties": {
                        "kind": "turbine",
                        "label": t.label,
                        "z": t.z,
                        "turbine_model": t.turbine_model.name if t.turbine_model_id else None,
                    },
                }
            )
        for b in boundaries:
            features.append(
                {
                    "type": "Feature",
                    "geometry": b.geometry,
                    "properties": {"kind": b.kind, "name": b.name},
                }
            )
        return Response({"type": "FeatureCollection", "features": features})
