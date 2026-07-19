from django.contrib import admin

from apps.files.models import FileObject


@admin.register(FileObject)
class FileObjectAdmin(admin.ModelAdmin):
    list_display = ("original_name", "project", "size_bytes", "uploaded_by", "created_at")
    search_fields = ("original_name", "checksum_sha256")
