from django.urls import path

from apps.gis.api.export_views import ProjectTurbinesCSVExportView
from apps.gis.api.layout_views import (
    ProjectBoundaryListCreateView,
    ProjectLayoutGeoJSONView,
    ProjectSpacingCheckView,
    ProjectSpatialValidationView,
)
from apps.gis.api.turbine_views import (
    ProjectTurbineDetailView,
    ProjectTurbineDistancesView,
    ProjectTurbineImportView,
    ProjectTurbineListCreateView,
    TurbineCatalogueImportView,
    TurbineManufacturerListCreateView,
    TurbineModelListView,
)
from apps.gis.api.views import CRSListCreateView, ProjectCRSListCreateView, TransformView

urlpatterns = [
    path("gis/crs/", CRSListCreateView.as_view(), name="gis-crs"),
    path(
        "projects/<uuid:project_id>/crs/",
        ProjectCRSListCreateView.as_view(),
        name="project-crs",
    ),
    path("gis/transform/", TransformView.as_view(), name="gis-transform"),
    path("gis/turbine-models/", TurbineModelListView.as_view(), name="turbine-models"),
    path(
        "gis/turbine-manufacturers/",
        TurbineManufacturerListCreateView.as_view(),
        name="turbine-manufacturers",
    ),
    path(
        "gis/turbine-catalogue/import/",
        TurbineCatalogueImportView.as_view(),
        name="turbine-catalogue-import",
    ),
    path(
        "projects/<uuid:project_id>/turbines/",
        ProjectTurbineListCreateView.as_view(),
        name="project-turbines",
    ),
    path(
        "projects/<uuid:project_id>/turbines/import/",
        ProjectTurbineImportView.as_view(),
        name="project-turbines-import",
    ),
    path(
        "projects/<uuid:project_id>/turbines/distances/",
        ProjectTurbineDistancesView.as_view(),
        name="project-turbine-distances",
    ),
    path(
        "projects/<uuid:project_id>/turbines/spacing-check/",
        ProjectSpacingCheckView.as_view(),
        name="project-turbine-spacing",
    ),
    path(
        "projects/<uuid:project_id>/turbines/<uuid:turbine_id>/",
        ProjectTurbineDetailView.as_view(),
        name="project-turbine-detail",
    ),
    path(
        "projects/<uuid:project_id>/boundaries/",
        ProjectBoundaryListCreateView.as_view(),
        name="project-boundaries",
    ),
    path(
        "projects/<uuid:project_id>/spatial-validation/",
        ProjectSpatialValidationView.as_view(),
        name="project-spatial-validation",
    ),
    path(
        "projects/<uuid:project_id>/layout.geojson",
        ProjectLayoutGeoJSONView.as_view(),
        name="project-layout-geojson",
    ),
    path(
        "projects/<uuid:project_id>/turbines.csv",
        ProjectTurbinesCSVExportView.as_view(),
        name="project-turbines-csv",
    ),
]
