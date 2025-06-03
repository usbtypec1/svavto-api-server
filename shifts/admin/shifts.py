from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.translation import gettext, gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.services import get_current_shift_date
from shifts.exceptions import StaffHasActiveShiftError
from shifts.models import CarToWash, Shift, ShiftFinishPhoto
from shifts.services.shifts.validators import ensure_staff_has_no_active_shift


class CurrentShiftFilter(admin.SimpleListFilter):
    title = _("current shift")
    parameter_name = "current_shift"

    def lookups(self, request, model_admin):
        return (("true", _("yes")),)

    def queryset(self, request, queryset):
        current_shift_date = get_current_shift_date()
        if self.value() == "true":
            return queryset.filter(date=current_shift_date)
        return queryset


class IsStartedFilter(admin.SimpleListFilter):
    title = _("started")
    parameter_name = "started"

    def lookups(self, request, model_admin):
        return (
            ("true", _("yes")),
            ("false", _("no")),
        )

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(started_at__isnull=False)

        if self.value() == "false":
            return queryset.filter(started_at__isnull=True)


class IsFinishedFilter(admin.SimpleListFilter):
    title = _("finished")
    parameter_name = "finished"

    def lookups(self, request, model_admin):
        return (
            ("true", _("yes")),
            ("false", _("no")),
        )

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "true":
            return queryset.filter(finished_at__isnull=False)

        if self.value() == "false":
            return queryset.filter(finished_at__isnull=True)


class ShiftResource(resources.ModelResource):
    class Meta:
        model = Shift


class ShiftFinishPhotoInline(admin.TabularInline):
    model = ShiftFinishPhoto
    extra = 0


class CarToWashInline(admin.TabularInline):
    model = CarToWash
    extra = 0
    show_change_link = True


@admin.register(Shift)
class ShiftAdmin(ImportExportModelAdmin):
    resource_class = ShiftResource
    readonly_fields = ("id",)
    list_display = (
        "staff",
        "date",
        "car_wash",
        "started_at",
        "finished_at",
        "created_at",
    )
    list_select_related = ("staff", "car_wash")
    ordering = ("-date",)
    list_filter = (
        "car_wash",
        "is_extra",
        "is_test",
        CurrentShiftFilter,
        IsStartedFilter,
        IsFinishedFilter,
    )
    inlines = (ShiftFinishPhotoInline, CarToWashInline)
    search_fields = ("id", "date", "staff__full_name", "staff__id")
    search_help_text = _("Search by shift ID or date, staff ID or full name")
    date_hierarchy = "date"
    autocomplete_fields = ("staff", "car_wash")

    def save_model(self, request, obj, form, change):
        is_creating = not change
        if is_creating:
            try:
                ensure_staff_has_no_active_shift(obj.staff_id)
            except StaffHasActiveShiftError:
                messages.set_level(request, messages.ERROR)
                messages.error(request, gettext("staff has active shift"))
                return
        super().save_model(request, obj, form, change)
