from django.db import models
from django.utils.translation import gettext_lazy as _


class Text(models.Model):
    class Type(models.TextChoices):
        TRANSFERRED_CAR_NUMBER_HELP_TEXT = (
            "transferred_car_number_help_text",
            _("Transferred car number help text"),
        )
        TRANSFERRED_CAR_CLASS_HELP_TEXT = (
            "transferred_car_class_help_text",
            _("Transferred car class help text"),
        )

    key = models.CharField(
        max_length=255,
        unique=True,
        choices=Type.choices,
        verbose_name=_("Key"),
    )
    value = models.TextField(max_length=1024, verbose_name=_("Value"))

    def __str__(self):
        return self.get_key_display()

    class Meta:
        verbose_name = _("Text")
        verbose_name_plural = _("Texts")
