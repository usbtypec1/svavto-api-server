from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShiftsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shifts'
    verbose_name = _('shift')
