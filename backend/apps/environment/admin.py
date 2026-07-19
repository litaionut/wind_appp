from django.contrib import admin

from apps.environment.models import ImpactRun, Receptor

admin.site.register(Receptor)
admin.site.register(ImpactRun)
