from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateTimeRangeFilterBuilder

from shifts.models import CarToWashAdditionalService


class CarToWashAdditionalServiceResource(resources.ModelResource):
    staff = fields.Field(
        "car__shift__staff__full_name",
        column_name=_("staff"),
    )
    shift_date = fields.Field(
        "car__shift__date",
        column_name=_("shift date"),
    )
    service_name = fields.Field(
        "service__name",
        column_name=_("car wash service name"),
    )
    car_number = fields.Field(
        "car__number",
        column_name=_("car number"),
    )

    class Meta:
        model = CarToWashAdditionalService


@admin.register(CarToWashAdditionalService)
class CarToWashAdditionalServiceAdmin(ImportExportModelAdmin):
    resource_class = CarToWashAdditionalServiceResource
    list_display = ("staff", "shift_date", "car", "service", "count")
    list_select_related = ("car", "service", "car__shift", "car__shift__staff")
    list_filter = (
        "service__is_countable",
        "service__is_dry_cleaning",
        (
            "car__shift__date",
            DateTimeRangeFilterBuilder(
                title=_("shift date"),
            ),
        ),
        "service__name",
    )
    autocomplete_fields = (
        "car",
        "service",
    )
    search_fields = ("car__shift__id__iexact", "car__number", "service__name")
    search_help_text = _("search by shift ID, car number, service name")

    @admin.display(description=_("staff"))
    def staff(self, obj: CarToWashAdditionalService):
        return obj.car.shift.staff.full_name

    @admin.display(description=_("shift date"))
    def shift_date(self, obj: CarToWashAdditionalService):
        return obj.car.shift.date
