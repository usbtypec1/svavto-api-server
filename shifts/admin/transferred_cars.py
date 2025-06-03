from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from rangefilter.filters import DateTimeRangeFilterBuilder

from shifts.models import CarToWash, CarToWashAdditionalService


class CarToWashAdditionalServiceInline(admin.TabularInline):
    model = CarToWashAdditionalService
    extra = 0
    show_change_link = True


class CarToWashResource(resources.ModelResource):
    car_wash = resources.Field(
        attribute="shift__car_wash__name",
        column_name=_("car wash"),
    )
    shift_date = resources.Field(
        attribute="shift__date",
        column_name=_("shift date"),
    )
    staff = resources.Field(
        attribute="shift__staff__full_name",
        column_name=_("staff"),
    )
    number = resources.Field(attribute="number", column_name=_("car number"))
    car_class = resources.Field(
        attribute="car_class", column_name=_("car class")
    )
    wash_type = resources.Field(
        attribute="wash_type",
        column_name=_("wash type"),
    )
    windshield_washer_refilled_bottle_percentage = resources.Field(
        attribute="windshield_washer_refilled_bottle_percentage",
        column_name=_("windshield washer refilled bottle percentage"),
    )
    transfer_price = resources.Field(
        attribute="transfer_price",
        column_name=_("transfer price at the moment"),
    )
    comfort_class_car_washing_price = resources.Field(
        attribute="comfort_class_car_washing_price",
        column_name=_("price of comfort class car washing at the moment"),
    )
    business_class_car_washing_price = resources.Field(
        attribute="business_class_car_washing_price",
        column_name=_("price of business class car washing at the moment"),
    )
    van_washing_price = resources.Field(
        attribute="van_washing_price",
        column_name=_("price of van washing at the moment"),
    )
    windshield_washer_price_per_bottle = resources.Field(
        attribute="windshield_washer_price_per_bottle",
        column_name=_("price of windshield washer per bottle at the moment"),
    )
    created_at = resources.Field(
        attribute="created_at",
        column_name=_("created at"),
    )

    class Meta:
        model = CarToWash
        fields = (
            "id",
            "car_wash",
            "shift_date",
            "staff",
            "number",
            "car_class",
            "wash_type",
            "windshield_washer_refilled_bottle_percentage",
            "transfer_price",
            "comfort_class_car_washing_price",
            "business_class_car_washing_price",
            "van_washing_price",
            "windshield_washer_price_per_bottle",
            "created_at",
        )


@admin.register(CarToWash)
class CarToWashAdmin(ExportActionModelAdmin, ImportExportModelAdmin):
    resource_class = CarToWashResource
    readonly_fields = ("id",)
    inlines = (CarToWashAdditionalServiceInline,)
    list_display = (
        "number",
        "car_wash",
        "shift",
        "car_class",
        "wash_type",
    )
    list_display_links = (
        "number",
        "car_wash",
        "shift",
        "car_class",
        "wash_type",
    )
    list_filter = (
        "car_class",
        "car_wash",
        "wash_type",
        (
            "shift__date",
            DateTimeRangeFilterBuilder(
                title=_("shift date"),
            ),
        ),
    )
    search_fields = (
        "shift__id",
        "number",
        "shift__date",
    )
    search_help_text = _("search by shift ID, car number and shift date")
    list_select_related = ("shift", "car_wash")
    list_per_page = 100
