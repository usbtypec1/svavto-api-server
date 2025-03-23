from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DepositsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deposits'
    verbose_name = _('Deposits')
