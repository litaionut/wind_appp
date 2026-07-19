"""Django admin for audit events (read-oriented)."""

from django.contrib import admin

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "organization", "project", "created_at")
    list_filter = ("action",)
    search_fields = ("action", "entity_type", "entity_id", "actor__username")
    readonly_fields = (
        "id",
        "action",
        "actor",
        "organization",
        "project",
        "entity_type",
        "entity_id",
        "metadata",
        "ip_address",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser
