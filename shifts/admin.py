from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ExportActionModelAdmin, ExportMixin

from shifts.models import (
    AvailableDate,
    CarToWash,
    CarToWashAdditionalService,
    Shift,
)


class CarToWashResource(resources.ModelResource):
    car_wash = resources.Field(
        attribute='shift__car_wash__name',
        column_name=_('Car wash'),
    )
    shift_date = resources.Field(
        attribute='shift__date',
        column_name=_('Shift date'),
    )
    staff = resources.Field(
        attribute='shift__staff__full_name',
        column_name=_('Staff'),
    )
    number = resources.Field(attribute='number', column_name=_('Car number'))
    car_class = resources.Field(
        attribute='car_class',
        column_name=_('Car class')
    )
    wash_type = resources.Field(
        attribute='wash_type',
        column_name=_('Wash type'),
    )
    windshield_washer_refilled_bottle_percentage = resources.Field(
        attribute='windshield_washer_refilled_bottle_percentage',
        column_name=_('Windshield washer refilled bottle percentage'),
    )
    transfer_price = resources.Field(
        attribute='transfer_price',
        column_name=_('Transfer price at the moment'),
    )
    comfort_class_car_washing_price = resources.Field(
        attribute='comfort_class_car_washing_price',
        column_name=_('Price of comfort class car washing at the moment')
    )
    business_class_car_washing_price = resources.Field(
        attribute='business_class_car_washing_price',
        column_name=_('Price of business class car washing at the moment')
    )
    van_washing_price = resources.Field(
        attribute='van_washing_price',
        column_name=_('Price of van washing at the moment')
    )
    windshield_washer_price_per_bottle = resources.Field(
        attribute='windshield_washer_price_per_bottle',
        column_name=_('Price of windshield washer per bottle at the moment')
    )
    created_at = resources.Field(
        attribute='created_at',
        column_name=_('Created at'),
    )

    class Meta:
        model = CarToWash
        fields = (
            'car_wash',
            'shift_date',
            'staff',
            'number',
            'car_class',
            'wash_type',
            'windshield_washer_refilled_bottle_percentage',
            'transfer_price',
            'comfort_class_car_washing_price',
            'business_class_car_washing_price',
            'van_washing_price',
            'windshield_washer_price_per_bottle',
            'created_at',
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
class CarToWashAdmin(ExportActionModelAdmin):
    resource_class = CarToWashResource
    readonly_fields = ('id',)
    inlines = (CarToWashAdditionalServiceInline,)
    list_display = ('number', 'car_class', 'wash_type')
    list_filter = ('car_class', 'wash_type')
    list_select_related = ('shift',)


@admin.register(CarToWashAdditionalService)
class CarToWashAdditionalServiceAdmin(admin.ModelAdmin):
    list_display = ('car', 'service', 'count')
    list_select_related = ('car',)
