from typing import Final

from django.db import models
from django.utils.translation import gettext as _


DEFAULT_SHIFT_CARS_THRESHOLD: Final[int] = 8


class ShiftCarsThreshold(models.Model):
    value = models.PositiveSmallIntegerField(
        verbose_name=_("Value"),
        help_text=_(
            "The minimum number of cars that must be transferred during a "
            "shift."
        ),
        default=DEFAULT_SHIFT_CARS_THRESHOLD,
    )

    def __str__(self):
        return _("Shift cars threshold: %(value)s") % {"value": self.value}

    class Meta:
        verbose_name = _("Shift cars threshold")
        verbose_name_plural = _("Shift cars threshold")

    @classmethod
    def get(cls) -> int:
        threshold = cls.objects.first()
        if threshold is not None:
            return threshold.value
        return DEFAULT_SHIFT_CARS_THRESHOLD
