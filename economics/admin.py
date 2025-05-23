from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from rangefilter.filters import DateTimeRangeFilterBuilder

from core.admin import SingleRowMixin
from economics.models import (
    CarTransporterAndWasherServicePrices, CarTransporterPenalty,
    CarTransporterServicePrices, CarTransporterSurcharge, CarWashPenalty,
    CarWashSurcharge, PenaltyPhoto,
)


class CarWashPenaltyResource(ModelResource):
    class Meta:
        model = CarWashPenalty


class CarWashSurchargeResource(ModelResource):
    class Meta:
        model = CarWashSurcharge


class CarTransporterPenaltyResource(ModelResource):
    class Meta:
        model = CarTransporterPenalty
        fields = (
            "id",
            "staff__id",
            "staff__full_name",
            "date",
            "reason",
            "amount",
            "consequence",
            "created_at",
        )


class CarTransporterSurchargeResource(ModelResource):
    class Meta:
        model = CarTransporterSurcharge
        fields = (
            "id",
            "staff__id",
            "staff__full_name",
            "date",
            "reason",
            "amount",
            "created_at",
        )


@admin.register(PenaltyPhoto)
class PenaltyPhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(CarTransporterPenalty)
class CarTransporterPenaltyAdmin(ImportExportModelAdmin):
    resource_class = CarTransporterPenaltyResource
    list_display = (
        "staff",
        "reason",
        "amount",
        "consequence",
        "date",
    )
    date_hierarchy = "date"
    autocomplete_fields = ("staff",)
    list_select_related = ("staff",)
    list_filter = (
        (
            "date",
            DateTimeRangeFilterBuilder(
                title=_('Date'),
            )
        ),
        "staff",
        "reason",
        "consequence",
    )
    search_fields = ("staff__full_name", "staff__id", "reason")
    search_help_text = "Search by staff full name, staff id, reason"


@admin.register(CarTransporterSurcharge)
class CarTransporterSurchargeAdmin(ImportExportModelAdmin):
    resource_class = CarTransporterSurchargeResource
    list_display = (
        "staff",
        "reason",
        "amount",
        "date",
    )
    date_hierarchy = "date"
    autocomplete_fields = ("staff",)
    list_select_related = ("staff",)
    list_filter = (
        (
            "date",
            DateTimeRangeFilterBuilder(
                title=_('Date'),
            )
        ),
        "staff",
        "reason",
    )
    search_fields = ("staff__full_name", "staff__id", "reason")
    search_help_text = "Search by staff full name, staff id, reason"


@admin.register(CarWashPenalty)
class CarWashPenaltyAdmin(ImportExportModelAdmin):
    resource_class = CarWashPenaltyResource
    list_display = (
        "car_wash",
        "reason",
        "amount",
        "created_at",
    )
    autocomplete_fields = ("car_wash",)
    list_filter = (
        (
            "date",
            DateTimeRangeFilterBuilder(
                title=_('Date'),
            )
        ),
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
    autocomplete_fields = ("car_wash",)
    list_filter = (
        (
            "date",
            DateTimeRangeFilterBuilder(
                title=_('Date'),
            )
        ),
        "car_wash",
        "reason",
    )
    search_fields = ("car_wash__name", "reason")
    search_help_text = "Search by car wash name, reason"


@admin.register(CarTransporterAndWasherServicePrices)
class CarTransporterAndWasherServicePricesAdmin(
    SingleRowMixin,
    admin.ModelAdmin,
):
    pass


@admin.register(CarTransporterServicePrices)
class CarTransporterServicePricesAdmin(SingleRowMixin, admin.ModelAdmin):
    pass
