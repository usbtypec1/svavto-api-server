from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from economics.models import Penalty, StaffServicePrice, Surcharge


class PenaltyResource(ModelResource):
    class Meta:
        model = Penalty


class SurchargeResource(ModelResource):
    class Meta:
        model = Surcharge


@admin.register(Penalty)
class PenaltyAdmin(ImportExportModelAdmin):
    resource_class = PenaltyResource
    list_display = (
        'staff',
        'reason',
        'amount',
        'consequence',
        'created_at',
    )
    list_select_related = ('staff',)
    list_filter = (
        'staff',
        'reason',
        'consequence',
    )
    search_fields = ('staff__full_name', 'staff__id', 'reason')
    search_help_text = 'Search by staff full name, staff id, reason'


@admin.register(Surcharge)
class SurchargeAdmin(ImportExportModelAdmin):
    resource_class = SurchargeResource
    list_display = (
        'staff',
        'reason',
        'amount',
        'created_at',
    )
    list_select_related = ('staff',)
    list_filter = (
        'staff',
        'reason',
    )
    search_fields = ('staff__full_name', 'staff__id', 'reason')
    search_help_text = 'Search by staff full name, staff id, reason'


@admin.register(StaffServicePrice)
class StaffServicePriceAdmin(admin.ModelAdmin):
    list_display = (
        'service',
        'price',
        'updated_at',
    )
    ordering = ('service',)
    readonly_fields = ('service', 'updated_at')

    def has_add_permission(self, request):
        return False
