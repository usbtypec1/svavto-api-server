from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as __, gettext as _

from staff.models import Staff


def report_period_number_validator(value: int) -> None:
    if value not in range(1, 3):
        raise ValidationError(_("Report period number must be 1 or 2."))


def month_validator(value: int) -> None:
    if value not in range(1, 13):
        raise ValidationError(_("Month must be between 1 and 12."))


class RetentionExclusion(models.Model):
    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=__("staff"),
    )
    year = models.PositiveSmallIntegerField(verbose_name=__("year"))
    month = models.PositiveSmallIntegerField(
        validators=(month_validator,),
        verbose_name=__("month"),
    )
    report_period_number = models.PositiveSmallIntegerField(
        validators=(report_period_number_validator,),
        verbose_name=__("report period number"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
