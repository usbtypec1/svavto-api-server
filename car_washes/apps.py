from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CarWashesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "car_washes"
    verbose_name = _("car wash")
