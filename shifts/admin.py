from django.contrib import admin
from django.db.models import QuerySet
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


class IsStartedFilter(admin.SimpleListFilter):
    title = _('started')
    parameter_name = 'started'

    def lookups(self, request, model_admin):
        return (
            ('true', _('Started')),
            ('false', _('Not started')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(started_at__isnull=False)

        if self.value() == 'false':
            return queryset.filter(started_at__isnull=True)


class IsFinishedFilter(admin.SimpleListFilter):
    title = _('finished')
    parameter_name = 'finished'

    def lookups(self, request, model_admin):
        return (
            ('true', _('Finished')),
            ('false', _('Not finished')),
        )

    def queryset(self, request, queryset: QuerySet):
        if self.value() == 'true':
            return queryset.filter(finished_at__isnull=False)

        if self.value() == 'false':
            return queryset.filter(finished_at__isnull=True)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        'staff',
        'date',
        'car_wash',
        'started_at',
        'finished_at',
        'created_at',
    )
    list_select_related = ('staff', 'car_wash')
    ordering = ('-date',)
    list_filter = (
        'car_wash',
        'staff',
        'is_extra',
        IsStartedFilter,
        IsFinishedFilter,
    )
    inlines = (CarToWashInline,)
    search_fields = ('staff__full_name', 'staff__id')
    search_help_text = _('You can search by staff name or staff id.')
    date_hierarchy = 'date'


@admin.register(CarToWash)
class CarToWashAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    inlines = (CarToWashAdditionalServiceInline,)
    list_display = ('number', 'car_class', 'wash_type')
    list_filter = ('car_class', 'wash_type')
    list_select_related = ('shift',)


@admin.register(CarToWashAdditionalService)
class CarToWashAdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ('car', 'name', 'count')
    list_select_related = ('car',)
