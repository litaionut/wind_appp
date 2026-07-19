"""Serializers for project membership management."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import OrganizationMembership
from apps.projects.models import ProjectMembership, ProjectRole

User = get_user_model()


class ProjectMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ("id", "username", "role", "created_at")
        read_only_fields = ("id", "username", "created_at")


class ProjectMembershipCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(
        choices=ProjectRole.choices,
        default=ProjectRole.PROJECT_VIEWER,
    )

    def validate_username(self, value: str) -> str:
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User not found.")
        return value

    def validate(self, attrs: dict) -> dict:
        project = self.context["project"]
        user = User.objects.get(username=attrs["username"])
        if not OrganizationMembership.objects.filter(
            organization=project.organization, user=user
        ).exists():
            raise serializers.ValidationError(
                "User must be a member of the organization first."
            )
        if ProjectMembership.objects.filter(project=project, user=user).exists():
            raise serializers.ValidationError("User is already a project member.")
        attrs["user"] = user
        return attrs
