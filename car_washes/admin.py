from django.contrib import admin
from car_washes.models import CarWash


@admin.register(CarWash)
class CarWashAdmin(admin.ModelAdmin):
    pass
