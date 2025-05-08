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


class CarWashResource(ModelResource):
    class Meta:
        model = CarWash


class CarWashServicePriceResource(ModelResource):
    class Meta:
        model = CarWashServicePrice


@admin.register(CarWashService)
class CarWashServiceAdmin(ImportExportModelAdmin):
    resource_class = CarWashServiceResource
    list_display = ("name", "parent", "priority", "max_count")
    list_select_related = ("parent",)
    search_fields = ("name", "id")
    search_help_text = _("search by name or id")
    readonly_fields = ("id", "created_at", "updated_at")
    list_filter = ("is_dry_cleaning", "is_countable")


@admin.register(CarWash)
class CarWashAdmin(ImportExportModelAdmin):
    resource_class = CarWashResource
    list_display = ("name", "created_at")
    search_fields = ("name",)
    inlines = (CarWashServicePriceInline,)
    readonly_fields = ("id",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    'windshield_washer_price_per_bottle',
                )
            },
        ),
        (
            _("Car transporters"),
            {
                "fields": (
                    'comfort_class_car_washing_price',
                    'business_class_car_washing_price',
                    'van_washing_price',
                )
            },
        ),
        (
            _("Car transporters and washers"),
            {
                "fields": (
                    'car_transporters_and_washers_comfort_class_price',
                    'car_transporters_and_washers_business_class_price',
                    'car_transporters_and_washers_van_price',
                )
            }
        )
    )


@admin.register(CarWashServicePrice)
class CarWashServicePriceAdmin(ImportExportModelAdmin):
    resource_class = CarWashServicePriceResource
    list_display = ("car_wash", "service", "price")
    list_select_related = ("car_wash", "service")
    list_filter = ("car_wash", "service")
    list_display_links = ("car_wash", "service", "price")
    search_fields = ("service__name", "service__parent__name", "service__id")
    autocomplete_fields = (
        "car_wash",
        "service",
    )
