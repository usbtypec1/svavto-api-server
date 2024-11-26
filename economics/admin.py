from django.contrib import admin

from economics.models import Penalty, StaffServicePrice, Surcharge


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
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
class SurchargeAdmin(admin.ModelAdmin):
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
