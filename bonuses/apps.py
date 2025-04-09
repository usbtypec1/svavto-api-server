from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BonusesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bonuses'
    verbose_name = _("Bonuses")
