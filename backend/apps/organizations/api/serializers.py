"""Organization API serializers."""

from rest_framework import serializers

from apps.organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "slug",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_by", "created_at", "updated_at")
