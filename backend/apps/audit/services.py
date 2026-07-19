"""Audit recording helpers."""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from apps.audit.models import AuditEvent


def client_ip(request: HttpRequest | None) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def record_event(
    *,
    action: str,
    actor=None,
    organization=None,
    project=None,
    entity_type: str = "",
    entity_id: str = "",
    metadata: dict[str, Any] | None = None,
    request: HttpRequest | None = None,
) -> AuditEvent:
    return AuditEvent.objects.create(
        action=action,
        actor=actor,
        organization=organization,
        project=project,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else "",
        metadata=metadata or {},
        ip_address=client_ip(request),
    )
