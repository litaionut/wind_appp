"""File API serializers."""

from rest_framework import serializers

from apps.files.models import FileObject


class FileObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileObject
        fields = (
            "id",
            "organization",
            "project",
            "original_name",
            "content_type",
            "size_bytes",
            "checksum_sha256",
            "uploaded_by",
            "created_at",
        )
        read_only_fields = fields
