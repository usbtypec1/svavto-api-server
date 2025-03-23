from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from economics.models import (
    CarTransporterPenalty,
    StaffServicePrice,
    CarTransporterSurcharge,
    CarWashPenalty,
    CarWashSurcharge,
    PenaltyPhoto,
)


class CarWashPenaltyResource(ModelResource):
    class Meta:
        model = CarWashPenalty


class CarWashSurchargeResource(ModelResource):
    class Meta:
        model = CarWashSurcharge


class PenaltyResource(ModelResource):
    class Meta:
        model = CarTransporterPenalty


class SurchargeResource(ModelResource):
    class Meta:
        model = CarTransporterSurcharge


@admin.register(PenaltyPhoto)
class PenaltyPhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(CarTransporterPenalty)
class PenaltyAdmin(ImportExportModelAdmin):
    resource_class = PenaltyResource
    list_display = (
        "shift__staff",
        "reason",
        "amount",
        "consequence",
        "created_at",
    )
    list_select_related = ("shift",)
    list_filter = (
        "shift__staff",
        "reason",
        "consequence",
    )
    search_fields = ("shift__staff__full_name", "shift__staff__id", "reason")
    search_help_text = "Search by staff full name, staff id, reason"


@admin.register(CarTransporterSurcharge)
class SurchargeAdmin(ImportExportModelAdmin):
    resource_class = SurchargeResource
    list_display = (
        "shift__staff",
        "reason",
        "amount",
        "created_at",
    )
    list_select_related = ("shift",)
    list_filter = (
        "shift__staff",
        "reason",
    )
    search_fields = ("shift__staff__full_name", "shift__staff__id", "reason")
    search_help_text = "Search by staff full name, staff id, reason"


@admin.register(StaffServicePrice)
class StaffServicePriceAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "price",
        "updated_at",
    )
    ordering = ("service",)
    readonly_fields = ("service", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, *args):
        return False


@admin.register(CarWashPenalty)
class CarWashPenaltyAdmin(ImportExportModelAdmin):
    resource_class = CarWashPenaltyResource
    list_display = (
        "car_wash",
        "reason",
        "amount",
        "created_at",
    )
    list_filter = (
        "car_wash",
        "reason",
    )
    search_fields = ("car_wash__name", "reason")
    search_help_text = "Search by car wash name, reason"


@admin.register(CarWashSurcharge)
class CarWashSurchargeAdmin(ImportExportModelAdmin):
    resource_class = CarWashSurchargeResource
    list_display = (
        "car_wash",
        "reason",
        "amount",
        "created_at",
    )
    list_filter = (
        "car_wash",
        "reason",
    )
    search_fields = ("car_wash__name", "reason")
    search_help_text = "Search by car wash name, reason"
