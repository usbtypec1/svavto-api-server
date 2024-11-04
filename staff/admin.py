from django.contrib import admin

from shifts.models import Shift
from staff.models import Staff


class ShiftInline(admin.TabularInline):
    model = Shift
    extra = 0


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    inlines = (ShiftInline,)
