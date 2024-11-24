from django.contrib import admin
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
    list_display = ('name', 'parent')
    list_select_related = ('parent',)
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CarWash)
class CarWashAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = (CarWashServicePriceInline,)


@admin.register(CarWashServicePrice)
class CarWashServicePriceAdmin(admin.ModelAdmin):
    list_display = ('car_wash', 'service', 'price')
    list_select_related = ('car_wash', 'service')
    list_filter = ('car_wash', 'service')
    list_display_links = ('car_wash', 'service', 'price')
    autocomplete_fields = ('car_wash', 'service',)
