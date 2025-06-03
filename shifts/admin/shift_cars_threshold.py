from django.contrib import admin
from django.utils import timezone

from core.admin import SingleRowMixin
from shifts.models import Shift, ShiftCarsThreshold


@admin.register(ShiftCarsThreshold)
class ShiftCarsThresholdAdmin(SingleRowMixin, admin.ModelAdmin):

    def has_add_permission(self, request):
        return not ShiftCarsThreshold.objects.exists()

    def save_model(self, request, obj: ShiftCarsThreshold, form, change):
        (
            Shift.objects
            .filter(date__gte=timezone.localdate())
            .update(transferred_cars_threshold=obj.value)
        )
        super().save_model(request, obj, form, change)
