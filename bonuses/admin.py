from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from bonuses.models import BonusSettings
from core.admin import SingleRowMixin


class BonusSettingsResource(ModelResource):
    class Meta:
        model = BonusSettings

    def handle_import_error(self, result, error, raise_errors=False):
        print(error)


@admin.register(BonusSettings)
class BonusSettingsAdmin(SingleRowMixin, ImportExportModelAdmin):
    resource_class = BonusSettingsResource
    list_display = ("min_cars_count", "bonus_amount", "is_bonus_enabled")
    list_display_links = ("min_cars_count", "bonus_amount")
    filter_horizontal = ("excluded_staff",)
    readonly_fields = ("is_bonus_enabled",)

    @admin.display(boolean=True, description=_("Bonus enabled"))
    def is_bonus_enabled(self, obj: BonusSettings):
        return obj.is_bonus_enabled

    def generate_log_entries(self, result, request):
        """Stub function to avoid logging errors"""
        pass
