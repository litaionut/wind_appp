from django.apps import AppConfig


class HybridConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hybrid"
    label = "hybrid"
    verbose_name = "Solar and hybrid"
