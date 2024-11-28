from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shifts.models import Shift
from staff.models import AdminStaff, Staff


class ShiftInline(admin.TabularInline):
    model = Shift
    extra = 0


class IsBannedFilter(admin.SimpleListFilter):
    title = _('banned')
    parameter_name = 'banned'

    def lookups(self, request, model_admin):
        return (
            ('true', _('yes')),
            ('false', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(banned_at__isnull=False)

        if self.value() == 'false':
            return queryset.filter(banned_at__isnull=True)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    inlines = (ShiftInline,)
    list_filter = (IsBannedFilter,)
    list_display = (
        'id',
        'full_name',
        'car_sharing_phone_number',
        'console_phone_number',
        'created_at',
    )


@admin.register(AdminStaff)
class AdminStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
