"""Project API serializers."""

from rest_framework import serializers

from apps.projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    organization_id = serializers.UUIDField(source="organization.id", read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "organization_id",
            "name",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization_id",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        )
