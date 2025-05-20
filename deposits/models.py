from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.utils.translation import gettext_lazy as _, gettext

from staff.models import Staff


def report_period_number_validator(value: int) -> None:
    if value not in range(1, 3):
        raise ValidationError(gettext("Report period number must be 1 or 2."))


def month_validator(value: int) -> None:
    if value not in range(1, 13):
        raise ValidationError(gettext("Month must be between 1 and 12."))


class FineDepositException(models.Model):

    class ReportPeriodNumber(models.IntegerChoices):
        FIRST_HALF = 1, _("First half of month")
        SECOND_HALF = 2, _("Second half of month")

    class Month(models.IntegerChoices):
        JANUARY = 1, _("January")
        FEBRUARY = 2, _("February")
        MARCH = 3, _("March")
        APRIL = 4, _("April")
        MAY = 5, _("May")
        JUNE = 6, _("June")
        JULY = 7, _("July")
        AUGUST = 8, _("August")
        SEPTEMBER = 9, _("September")
        OCTOBER = 10, _("October")
        NOVEMBER = 11, _("November")
        DECEMBER = 12, _("December")

    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=_("Staff"),
    )
    year = models.PositiveSmallIntegerField(verbose_name=_("Year"))
    month = models.PositiveSmallIntegerField(
        verbose_name=_("Month"),
        choices=Month.choices,
    )
    report_period_number = models.PositiveSmallIntegerField(
        verbose_name=_("Report period"),
        choices=ReportPeriodNumber.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Fine deposit exception")
        verbose_name_plural = _("Fine deposit exceptions")
        constraints = (
            UniqueConstraint(
                fields=("staff", "year", "month", "report_period_number"),
                name="unique_fine_deposit_exception",
            ),
        )


class RoadAccidentDepositException(models.Model):
    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=_("Staff"),
    )
    from_date = models.DateField(
        verbose_name=_("From date"),
    )
    to_date = models.DateField(verbose_name=_("To date"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("Road accident deposit exception")
        verbose_name_plural = _("Road accident deposit exceptions")
        constraints = (
            CheckConstraint(
                check=models.Q(from_date__lt=models.F("to_date")),
                name="from_date_less_than_to_date",
                violation_error_message=_(
                    "From date must be less than to date.",
                ),
            ),
        )
