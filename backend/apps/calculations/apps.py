from django.apps import AppConfig


class CalculationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.calculations"
    label = "calculations"
    verbose_name = "Calculations"

    def ready(self) -> None:
        from apps.calculations import signals  # noqa: F401
