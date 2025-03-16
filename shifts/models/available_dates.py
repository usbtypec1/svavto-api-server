from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("AvailableDate",)


class AvailableDate(models.Model):
    month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(limit_value=1, message="Month must be at least 1"),
            MaxValueValidator(
                limit_value=12,
                message="Month cannot be greater than 12",
            ),
        ],
        verbose_name=_("month"),
    )
    year = models.PositiveSmallIntegerField(verbose_name=_("year"))

    class Meta:
        verbose_name = _("available date")
        verbose_name_plural = _("available dates")
        unique_together = ("month", "year")
        ordering = ("year", "month")

    def __str__(self):
        return f"{self.year}-{self.month}"
