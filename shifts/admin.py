from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.translation import gettext, gettext_lazy as _
from import_export import resources, fields
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from rangefilter.filters import DateTimeRangeFilterBuilder

from shifts.exceptions import StaffHasActiveShiftError
from shifts.models import (
    AvailableDate,
    CarToWash,
    CarToWashAdditionalService,
    Shift,
    ShiftFinishPhoto,
)
from shifts.services.shifts import ensure_staff_has_no_active_shift


class CarToWashAdditionalServiceResource(resources.ModelResource):
    staff = fields.Field('car__shift__staff__full_name', column_name=_('staff'))
    shift_date = fields.Field('car__shift__date', column_name=_('shift date'))

    class Meta:
        model = CarToWashAdditionalService


class AvailableDateResource(resources.ModelResource):
    class Meta:
        model = AvailableDate


class ShiftResource(resources.ModelResource):
    class Meta:
        model = Shift


class ShiftFinishPhotoResource(resources.ModelResource):
    class Meta:
        model = ShiftFinishPhoto


class CarToWashResource(resources.ModelResource):
    car_wash = resources.Field(
        attribute='shift__car_wash__name',
        column_name=_('car wash'),
    )
    shift_date = resources.Field(
        attribute='shift__date',
        column_name=_('shift date'),
    )
    staff = resources.Field(
        attribute='shift__staff__full_name',
        column_name=_('staff'),
    )
    number = resources.Field(attribute='number', column_name=_('car number'))
    car_class = resources.Field(
        attribute='car_class',
        column_name=_('car class')
    )
    wash_type = resources.Field(
        attribute='wash_type',
        column_name=_('wash type'),
    )
    windshield_washer_refilled_bottle_percentage = resources.Field(
        attribute='windshield_washer_refilled_bottle_percentage',
        column_name=_('windshield washer refilled bottle percentage'),
    )
    transfer_price = resources.Field(
        attribute='transfer_price',
        column_name=_('transfer price at the moment'),
    )
    comfort_class_car_washing_price = resources.Field(
        attribute='comfort_class_car_washing_price',
        column_name=_('price of comfort class car washing at the moment')
    )
    business_class_car_washing_price = resources.Field(
        attribute='business_class_car_washing_price',
        column_name=_('price of business class car washing at the moment')
    )
    van_washing_price = resources.Field(
        attribute='van_washing_price',
        column_name=_('price of van washing at the moment')
    )
    windshield_washer_price_per_bottle = resources.Field(
        attribute='windshield_washer_price_per_bottle',
        column_name=_('price of windshield washer per bottle at the moment')
    )
    created_at = resources.Field(
        attribute='created_at',
        column_name=_('created at'),
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


class ShiftFinishPhotoInline(admin.TabularInline):
    model = ShiftFinishPhoto
    extra = 0


class CarToWashInline(admin.TabularInline):
    model = CarToWash
    extra = 0
    show_change_link = True


class CarToWashAdditionalServiceInline(admin.TabularInline):
    model = CarToWashAdditionalService
    extra = 0
    show_change_link = True


@admin.register(AvailableDate)
class AvailableDateAdmin(ImportExportModelAdmin):
    resource_class = AvailableDateResource
    list_display = ('year', 'month')
    list_filter = ('year', 'month')


class IsStartedFilter(admin.SimpleListFilter):
    title = _('started')
    parameter_name = 'started'

    def lookups(self, request, model_admin):
        return (
            ('true', _('started')),
            ('false', _('not started')),
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
            ('true', _('yes')),
            ('false', _('no')),
        )

    def queryset(self, request, queryset: QuerySet):
        if self.value() == 'true':
            return queryset.filter(finished_at__isnull=False)

        if self.value() == 'false':
            return queryset.filter(finished_at__isnull=True)


@admin.register(Shift)
class ShiftAdmin(ImportExportModelAdmin):
    resource_class = ShiftResource
    readonly_fields = ('id',)
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
    inlines = (ShiftFinishPhotoInline, CarToWashInline)
    search_fields = ('staff__full_name', 'staff__id')
    search_help_text = _('you can search by staff name or staff id')
    date_hierarchy = 'date'
    autocomplete_fields = ('staff', 'car_wash')

    def save_model(self, request, obj, form, change):
        is_creating = not change
        if is_creating:
            try:
                ensure_staff_has_no_active_shift(obj.staff_id)
            except StaffHasActiveShiftError:
                messages.set_level(request, messages.ERROR)
                messages.error(request, gettext('staff has active shift'))
                return
        super().save_model(request, obj, form, change)


@admin.register(CarToWash)
class CarToWashAdmin(ExportActionModelAdmin, ImportExportModelAdmin):
    resource_class = CarToWashResource
    readonly_fields = ('id',)
    inlines = (CarToWashAdditionalServiceInline,)
    list_display = (
        'number',
        'car_wash',
        'shift',
        'car_class',
        'wash_type',
    )
    list_display_links = (
        'number',
        'car_wash',
        'shift',
        'car_class',
        'wash_type',
    )
    list_filter = (
        'car_class',
        'car_wash',
        'wash_type',
        ('shift__date', DateTimeRangeFilterBuilder(
            title=_('shift date'),
        )),
    )
    search_fields = ('number', 'shift__date',)
    search_help_text = _('search by number and shift date')
    list_select_related = ('shift', 'car_wash')
    list_per_page = 100


@admin.register(CarToWashAdditionalService)
class CarToWashAdditionalServiceAdmin(ImportExportModelAdmin):
    resource_class = CarToWashAdditionalServiceResource
    list_display = ('staff', 'shift_date', 'car', 'service', 'count')
    list_select_related = ('car', 'service', 'car__shift', 'car__shift__staff')
    list_filter = (
        'service__is_countable',
        'service__is_dry_cleaning',
        ('car__shift__date', DateTimeRangeFilterBuilder(
            title=_('shift date'),
        )),
        'service__name',
    )
    autocomplete_fields = ('car', 'service',)
    search_fields = ('car__shift__id__iexact', 'car__number', 'service__name')
    search_help_text = _('search by shift ID, car number, service name')

    @admin.display(description=_('staff'))
    def staff(self, obj: CarToWashAdditionalService):
        return obj.car.shift.staff.full_name

    @admin.display(description=_('shift date'))
    def shift_date(self, obj: CarToWashAdditionalService):
        return obj.car.shift.date


@admin.register(ShiftFinishPhoto)
class ShiftFinishPhotoAdmin(ImportExportModelAdmin):
    resource_class = ShiftFinishPhotoResource
    list_display = ('shift', 'file_id')
    list_select_related = ('shift',)
