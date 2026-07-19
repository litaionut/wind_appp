from django.urls import path

from apps.gis.api.views import CRSListCreateView, ProjectCRSListCreateView, TransformView

urlpatterns = [
    path("gis/crs/", CRSListCreateView.as_view(), name="gis-crs"),
    path(
        "projects/<uuid:project_id>/crs/",
        ProjectCRSListCreateView.as_view(),
        name="project-crs",
    ),
    path("gis/transform/", TransformView.as_view(), name="gis-transform"),
]
