from django.contrib import admin

from core.admin import SingleRowMixin
from shifts.models import WindshieldWasherHidden


@admin.register(WindshieldWasherHidden)
class WindshieldWasherHideAdmin(SingleRowMixin, admin.ModelAdmin):
    pass
