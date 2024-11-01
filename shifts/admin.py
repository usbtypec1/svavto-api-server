from django.contrib import admin

from shifts.models import Shift, CarToWash, CarToWashAdditionalService


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'car_wash')
    list_select_related = ('staff', 'car_wash')


@admin.register(CarToWash)
class CarToWashAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


@admin.register(CarToWashAdditionalService)
class CarToWashAdditionalServiceAdmin(admin.ModelAdmin):
    pass
