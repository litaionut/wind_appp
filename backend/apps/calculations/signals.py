"""Ensure stub calculation method exists after migrations."""

from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_stub_method(sender, **kwargs) -> None:
    if sender.name != "apps.calculations":
        return
    from apps.calculations.models import CalculationMethod, MethodStatus

    CalculationMethod.objects.get_or_create(
        method_id="platform_stub",
        version="v1",
        defaults={
            "title": "Platform stub calculation",
            "description": "Deterministic stub used for Release 0 validation.",
            "status": MethodStatus.APPROVED_DEFAULT,
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"},
        },
    )
