from shifts.models import Shift


class ShiftModelStaffSelectRelatedMixin:

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "shift":
            kwargs["queryset"] = Shift.objects.select_related("staff")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
