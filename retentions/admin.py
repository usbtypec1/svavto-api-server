from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from retentions.models import RetentionExclusion


@admin.register(RetentionExclusion)
class RetentionExclusionAdmin(ImportExportModelAdmin):
    list_display = ("staff", "from_date", "to_date", "created_at")
    search_fields = ("staff__first_name", "staff__last_name")
    list_filter = ("from_date", "to_date")
    date_hierarchy = "from_date"
    ordering = ("-from_date",)
