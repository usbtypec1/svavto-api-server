from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from shifts.models import AvailableDate


class AvailableDateResource(resources.ModelResource):
    class Meta:
        model = AvailableDate


@admin.register(AvailableDate)
class AvailableDateAdmin(ImportExportModelAdmin):
    resource_class = AvailableDateResource
    list_display = ("year", "month")
    list_filter = ("year", "month")
