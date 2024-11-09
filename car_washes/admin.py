from django.contrib import admin
from car_washes.models import CarWash, CarWashService


@admin.register(CarWashService)
class CarWashServiceAdmin(admin.ModelAdmin):
    autocomplete_fields = ('car_wash',)
    list_display = ('name', 'price', 'car_wash')


class CarWashServiceInline(admin.TabularInline):
    model = CarWashService
    extra = 0


@admin.register(CarWash)
class CarWashAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    inlines = (CarWashServiceInline,)
    search_fields = ('name',)
