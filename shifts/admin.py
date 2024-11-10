from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shifts.models import (
    Shift,
    CarToWash,
    CarToWashAdditionalService,
    AvailableDate,
)


class CarToWashInline(admin.TabularInline):
    model = CarToWash
    extra = 0


class CarToWashAdditionalServiceInline(admin.TabularInline):
    model = CarToWashAdditionalService
    extra = 0


@admin.register(AvailableDate)
class AvailableDateAdmin(admin.ModelAdmin):
    list_display = ('year', 'month')
    list_filter = ('year', 'month')


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'car_wash')
    list_select_related = ('staff', 'car_wash')
    ordering = ('-date',)
    list_filter = ('car_wash', 'staff')
    inlines = (CarToWashInline,)
    search_fields = ('staff__full_name', 'staff__id')
    search_help_text = _('You can search by staff name or staff id.')
    date_hierarchy = 'date'


@admin.register(CarToWash)
class CarToWashAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    inlines = (CarToWashAdditionalServiceInline,)
    list_display = ('number', 'shift__date', 'car_class', 'wash_type')
    list_filter = ('car_class', 'wash_type')
    list_select_related = ('shift',)


@admin.register(CarToWashAdditionalService)
class CarToWashAdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ('car', 'name', 'count')
    list_select_related = ('car',)
