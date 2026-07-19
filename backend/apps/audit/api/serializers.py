"""Audit API serializers."""

from rest_framework import serializers

from apps.audit.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True, default=None)

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "action",
            "actor",
            "actor_username",
            "organization",
            "project",
            "entity_type",
            "entity_id",
            "metadata",
            "ip_address",
            "created_at",
        )
        read_only_fields = fields
