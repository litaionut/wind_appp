"""File API URL routes."""

from django.urls import path

from apps.files.api.views import FileDetailView, FileDownloadView, ProjectFileListCreateView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/files/",
        ProjectFileListCreateView.as_view(),
        name="project-files",
    ),
    path("files/<uuid:file_id>/", FileDetailView.as_view(), name="file-detail"),
    path(
        "files/<uuid:file_id>/download/",
        FileDownloadView.as_view(),
        name="file-download",
    ),
]
