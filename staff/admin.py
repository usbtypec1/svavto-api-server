from django.contrib import admin

from staff.models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    pass
