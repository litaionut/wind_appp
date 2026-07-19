"""Serializers for organization membership management."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import OrganizationMembership, OrganizationRole

User = get_user_model()


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ("id", "username", "role", "created_at")
        read_only_fields = ("id", "username", "created_at")


class OrganizationMembershipCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(
        choices=OrganizationRole.choices,
        default=OrganizationRole.ORG_MEMBER,
    )

    def validate_username(self, value: str) -> str:
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User not found.")
        return value

    def validate(self, attrs: dict) -> dict:
        organization = self.context["organization"]
        user = User.objects.get(username=attrs["username"])
        if OrganizationMembership.objects.filter(
            organization=organization, user=user
        ).exists():
            raise serializers.ValidationError("User is already a member.")
        attrs["user"] = user
        return attrs
