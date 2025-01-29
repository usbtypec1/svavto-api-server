from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from car_washes.models import CarWash, CarWashService, CarWashServicePrice


class CarWashServicePriceInline(admin.TabularInline):
    model = CarWashServicePrice
    extra = 0


class CarWashServiceResource(ModelResource):
    class Meta:
        model = CarWashService


@admin.register(CarWashService)
class CarWashServiceAdmin(ImportExportModelAdmin):
    resource_class = CarWashServiceResource
    list_display = ('name', 'parent', 'priority')
    list_select_related = ('parent',)
    search_fields = ('name', 'id')
    search_help_text = _('search by name or id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_filter = ('is_dry_cleaning', 'is_countable')


@admin.register(CarWash)
class CarWashAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = (CarWashServicePriceInline,)
    readonly_fields = ('id',)


@admin.register(CarWashServicePrice)
class CarWashServicePriceAdmin(admin.ModelAdmin):
    list_display = ('car_wash', 'service', 'price')
    list_select_related = ('car_wash', 'service')
    list_filter = ('car_wash', 'service')
    list_display_links = ('car_wash', 'service', 'price')
    search_fields = ('service__name', 'service__parent__name', 'service__id')
    autocomplete_fields = (
        'car_wash',
        'service',
    )
