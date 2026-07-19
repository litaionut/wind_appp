"""METEO API views."""

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.meteo.api.serializers import (
    CampaignCreateSerializer,
    CampaignSerializer,
    SensorCreateSerializer,
    SensorSerializer,
)
from apps.meteo.models import MeasurementCampaign
from apps.meteo.services import (
    MeteoImportError,
    availability_stats,
    detect_frozen,
    import_timeseries_csv,
    mean_air_density,
    wind_rose,
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


def _campaign_for_member(user, campaign_id) -> MeasurementCampaign:
    try:
        campaign = MeasurementCampaign.objects.select_related("project").get(id=campaign_id)
    except MeasurementCampaign.DoesNotExist as exc:
        raise NotFound() from exc
    _project_for_member(user, campaign.project_id)
    return campaign


class ProjectCampaignListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        campaigns = MeasurementCampaign.objects.filter(project=project).prefetch_related(
            "sensors"
        )
        return Response(CampaignSerializer(campaigns, many=True).data)

    def post(self, request: Request, project_id) -> Response:
        project = _project_for_member(request.user, project_id)
        _require_engineer(request.user, project)
        serializer = CampaignCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        campaign = serializer.save(project=project, created_by=request.user)
        record_event(
            action="meteo.campaign_created",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="measurement_campaign",
            entity_id=campaign.id,
            metadata={"name": campaign.name},
            request=request,
        )
        return Response(CampaignSerializer(campaign).data, status=status.HTTP_201_CREATED)


class CampaignSensorListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        return Response(SensorSerializer(campaign.sensors.all(), many=True).data)

    def post(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        _require_engineer(request.user, campaign.project)
        serializer = SensorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sensor = serializer.save(campaign=campaign)
        return Response(SensorSerializer(sensor).data, status=status.HTTP_201_CREATED)


class CampaignTimeseriesImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        _require_engineer(request.user, campaign.project)
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "This field is required."})
        try:
            result = import_timeseries_csv(campaign, upload.read().decode("utf-8-sig"))
        except MeteoImportError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        record_event(
            action="meteo.timeseries_imported",
            actor=request.user,
            organization=campaign.project.organization,
            project=campaign.project,
            entity_type="measurement_campaign",
            entity_id=campaign.id,
            metadata=result,
            request=request,
        )
        return Response(result)


class CampaignAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        return Response(availability_stats(campaign))


class CampaignFrozenCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        _require_engineer(request.user, campaign.project)
        window = int(request.data.get("window", 6))
        flagged = detect_frozen(campaign, window=window)
        return Response({"flagged_points": flagged, "window": window})


class CampaignWindRoseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        speed_code = request.query_params.get("speed_code")
        direction_code = request.query_params.get("direction_code")
        if not speed_code or not direction_code:
            raise ValidationError(
                {"detail": "Query params speed_code and direction_code are required."}
            )
        try:
            result = wind_rose(
                campaign, speed_code=speed_code, direction_code=direction_code
            )
        except MeteoImportError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        return Response(result)


class CampaignAirDensityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, campaign_id) -> Response:
        campaign = _campaign_for_member(request.user, campaign_id)
        temperature_code = request.query_params.get("temperature_code")
        pressure_code = request.query_params.get("pressure_code")
        if not temperature_code or not pressure_code:
            raise ValidationError(
                {
                    "detail": "Query params temperature_code and pressure_code are required."
                }
            )
        try:
            result = mean_air_density(
                campaign,
                temperature_code=temperature_code,
                pressure_code=pressure_code,
            )
        except MeteoImportError as exc:
            raise ValidationError({"detail": exc.message}) from exc
        return Response(result)
