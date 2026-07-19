from django.urls import path

from apps.meteo.api.views import (
    CampaignAirDensityView,
    CampaignAvailabilityView,
    CampaignFrozenCheckView,
    CampaignSensorListCreateView,
    CampaignTimeseriesImportView,
    CampaignWindRoseView,
    ProjectCampaignListCreateView,
)

urlpatterns = [
    path(
        "projects/<uuid:project_id>/meteo/campaigns/",
        ProjectCampaignListCreateView.as_view(),
        name="project-meteo-campaigns",
    ),
    path(
        "meteo/campaigns/<uuid:campaign_id>/sensors/",
        CampaignSensorListCreateView.as_view(),
        name="meteo-campaign-sensors",
    ),
    path(
        "meteo/campaigns/<uuid:campaign_id>/timeseries/import/",
        CampaignTimeseriesImportView.as_view(),
        name="meteo-timeseries-import",
    ),
    path(
        "meteo/campaigns/<uuid:campaign_id>/availability/",
        CampaignAvailabilityView.as_view(),
        name="meteo-availability",
    ),
    path(
        "meteo/campaigns/<uuid:campaign_id>/qc/frozen/",
        CampaignFrozenCheckView.as_view(),
        name="meteo-qc-frozen",
    ),
    path(
        "meteo/campaigns/<uuid:campaign_id>/wind-rose/",
        CampaignWindRoseView.as_view(),
        name="meteo-wind-rose",
    ),
    path(
        "meteo/campaigns/<uuid:campaign_id>/air-density/",
        CampaignAirDensityView.as_view(),
        name="meteo-air-density",
    ),
]
