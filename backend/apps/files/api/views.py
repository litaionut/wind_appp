"""File upload/list/download API."""

from django.http import FileResponse
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.files.api.serializers import FileObjectSerializer
from apps.files.models import FileObject
from apps.files.storage import build_storage_key, open_path, save_bytes
from apps.projects.models import Project, ProjectMembership, ProjectRole

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _get_project_for_member(user, project_id) -> Project:
    if user.is_superuser:
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist as exc:
            raise NotFound() from exc
    try:
        return Project.objects.filter(memberships__user=user).distinct().get(id=project_id)
    except Project.DoesNotExist as exc:
        raise NotFound() from exc


def _require_upload_role(user, project: Project) -> None:
    if user.is_superuser:
        return
    membership = ProjectMembership.objects.filter(project=project, user=user).first()
    if membership is None or membership.role not in {
        ProjectRole.PROJECT_ADMIN,
        ProjectRole.PROJECT_ENGINEER,
    }:
        raise PermissionDenied("Project admin or engineer role required to upload.")


class ProjectFileListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request: Request, project_id) -> Response:
        project = _get_project_for_member(request.user, project_id)
        files = FileObject.objects.filter(project=project)
        return Response(FileObjectSerializer(files, many=True).data)

    def post(self, request: Request, project_id) -> Response:
        project = _get_project_for_member(request.user, project_id)
        _require_upload_role(request.user, project)
        upload = request.FILES.get("file")
        if upload is None:
            raise ValidationError({"file": "This field is required."})
        content = upload.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise ValidationError({"file": "File exceeds maximum size of 10 MB."})
        storage_key = build_storage_key(
            project.organization_id, project.id, upload.name
        )
        size_bytes, checksum = save_bytes(storage_key, content)
        file_obj = FileObject.objects.create(
            organization=project.organization,
            project=project,
            original_name=upload.name,
            content_type=getattr(upload, "content_type", None) or "application/octet-stream",
            size_bytes=size_bytes,
            checksum_sha256=checksum,
            storage_key=storage_key,
            uploaded_by=request.user,
        )
        record_event(
            action="file.uploaded",
            actor=request.user,
            organization=project.organization,
            project=project,
            entity_type="file",
            entity_id=file_obj.id,
            metadata={"name": file_obj.original_name, "size_bytes": size_bytes},
            request=request,
        )
        return Response(FileObjectSerializer(file_obj).data, status=status.HTTP_201_CREATED)


class FileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, file_id) -> Response:
        file_obj = _get_file_for_member(request.user, file_id)
        return Response(FileObjectSerializer(file_obj).data)


class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, file_id) -> FileResponse:
        file_obj = _get_file_for_member(request.user, file_id)
        path = open_path(file_obj.storage_key)
        if not path.exists():
            raise NotFound("Stored file is missing.")
        return FileResponse(
            path.open("rb"),
            as_attachment=True,
            filename=file_obj.original_name,
            content_type=file_obj.content_type,
        )


def _get_file_for_member(user, file_id) -> FileObject:
    try:
        file_obj = FileObject.objects.select_related("project").get(id=file_id)
    except FileObject.DoesNotExist as exc:
        raise NotFound() from exc
    if user.is_superuser:
        return file_obj
    if not ProjectMembership.objects.filter(project=file_obj.project, user=user).exists():
        raise NotFound()
    return file_obj
