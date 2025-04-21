from typing import Self

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from staff.models import Staff


class BonusSettings(models.Model):
    min_cars_count = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name=_("Minimum cars count"),
        help_text=_(
            "Minimum number of cars required to apply the bonus."
            " Set to 0 to "
            "disable bonus."
        ),
    )
    bonus_amount = models.PositiveIntegerField(
        verbose_name=_("Bonus amount"),
        help_text=_(
            "Amount of bonus to be applied. Set to 0 to disable bonus."
        ),
    )
    excluded_staff = models.ManyToManyField(
        to=Staff,
        blank=True,
        verbose_name=_("Excluded from bonuses staff"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
    )

    class Meta:
        verbose_name = _("Bonus settings")
        verbose_name_plural = _("Bonus settings")

    def __str__(self):
        return gettext("Bonus settings")

    @property
    def is_bonus_enabled(self):
        return self.min_cars_count > 0 and self.bonus_amount > 0

    @classmethod
    def get_or_create(cls) -> Self:
        settings = cls.objects.prefetch_related('excluded_staff').first()
        if settings is None:
            settings = BonusSettings(
                min_cars_count=4,
                bonus_amount=300,
            )
            settings.full_clean()
            settings.save()
        return settings
